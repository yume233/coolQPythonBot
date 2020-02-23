from asyncio import (AbstractEventLoop, iscoroutinefunction,
                     run_coroutine_threadsafe)
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial, wraps
from time import time
from typing import Any, Awaitable, Callable, Optional

from nonebot import get_bot
from requests import HTTPError, RequestException

from ..exceptions import BotRequestError, ExceptionProcess
from ..log import logger
from ..settings.bot import settings
from .functions import getObjectName

_Executor = ThreadPoolExecutor(settings.THREAD_POOL_NUM)


def Timing(function: Callable) -> Callable:
    @wraps(function)
    def SyncWrapper(*args, **kwargs) -> Any:
        startTime = time() * 1000
        try:
            return function(*args, **kwargs)
        finally:
            logger.debug(
                f'The function {getObjectName(function)} is completed ' +
                f'and takes {time() * 1000 - startTime:.3f}ms.')

    @wraps(function)
    async def AsyncWrapper(*args, **kwargs) -> Any:
        startTime = time() * 1000
        try:
            return await function(*args, **kwargs)
        finally:
            logger.debug(
                f'The function {getObjectName(function)} is completed ' +
                f'and takes {time() * 1000 - startTime:.3f}ms.')

    return AsyncWrapper if iscoroutinefunction(function) else SyncWrapper


def SyncToAsync(function: Callable) -> Callable:
    function = Timing(function)

    @wraps(function)
    def wrapper(*args, **kwargs) -> Any:
        loop: AbstractEventLoop = get_bot().loop
        runner: Callable = lambda: function(*args, **kwargs)
        return loop.run_in_executor(_Executor, runner)

    return wrapper


def AsyncToSync(function: Callable) -> Callable:
    function = Timing(function)

    @wraps(function)
    def wrapper(*args, **kwargs) -> Any:
        assert iscoroutinefunction(function)
        loop: AbstractEventLoop = get_bot().loop
        coroutine: Awaitable = function(*args, **kwargs)
        future: Future = run_coroutine_threadsafe(coroutine, loop)
        return future.result()

    return wrapper


def CatchRequestsException(function: Callable = None,
                           *,
                           prompt: Optional[str] = None,
                           retries: Optional[int] = None) -> Callable:
    if function is None:
        return partial(CatchRequestsException, prompt=prompt, retries=retries)

    functionName = getObjectName(function)
    function = Timing(function)

    @wraps(function)
    def wrapper(*args, **kwargs) -> Any:
        for _ in range(retries if retries else 1):
            try:
                return function(*args, **kwargs)
            except RequestException as error:
                traceID = ExceptionProcess.catch()
                logger.debug(f'Function {functionName} encountered' +
                             f'a network request error: "{error}"')
                if isinstance(error, HTTPError): break
        raise BotRequestError(prompt, traceID)

    return wrapper
