from asyncio import Task, get_event_loop, set_event_loop
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial, wraps
from time import sleep, time
from typing import Callable, Optional, Union

from nonebot import IntentCommand, logger, on_natural_language
from requests import HTTPError, RequestException

from .botConfig import settings
from .exception import BotRequestError, ExceptionProcess

_EXECUTOR = ThreadPoolExecutor(settings.THREAD_POOL_NUM)
_EVENT_LOOP = get_event_loop()


def _getFunctionName(function: Callable) -> str:
    if hasattr(function, '__qualname__'):
        return function.__qualname__
    elif hasattr(function, '__name__'):
        return function.__name__
    else:
        return function.__repr__()


def Timeit(function: Callable):
    """Decorator for timing a function
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        functionName = _getFunctionName(function)
        startTime = time() * 1000
        try:
            returnData = function(*args, **kwargs)
        finally:
            runningCost = (time() * 1000) - startTime
            logger.debug(
                f'Function {functionName} cost {runningCost:.3f}ms.' +
                f'args={str(args):.100s}...,kwargs={str(kwargs):.100s}...')
        return returnData

    return wrapper


def SyncToAsync(function: Callable):
    """Decorator to convert synchronous functions to asynchronous functions
    """
    function = Timeit(function)

    @wraps(function)
    async def wrapper(*args, **kwargs):
        def runner():
            set_event_loop(_EVENT_LOOP)
            return function(*args, **kwargs)

        return await get_event_loop().run_in_executor(_EXECUTOR, runner)

    return wrapper


def AsyncToSync(function: Callable):
    """Decorator to convert asynchronous functions to synchronous functions
    """
    function = Timeit(function)

    @wraps(function)
    def wrapper(*args, **kwargs):
        task: Task = _EVENT_LOOP.create_task(function(*args, **kwargs))
        while not task.done():
            sleep(.1)
        if task.exception():
            raise task.exception()
        return task.result()

    return wrapper


Async = SyncToAsync
Sync = AsyncToSync


def WithKeyword(keywords: Union[str, tuple],
                command: str,
                confidence: Optional[Union[float, int]] = 80.0):
    """Decorator, set keywords for commands
    
    Parameters
    ----------
    keywords : Union[str, tuple]
        Keyword of the trigger command, which can be one or more
    command : str
        Command name
    confidence : Union[float, int], optional
        Confidence is used to identify the degree of ambiguity (unit:%), by default 80.0
    """
    def decorator(function: Callable):
        getKeyword = keywords if isinstance(keywords, tuple) else (keywords, )

        @on_natural_language(keywords=getKeyword)
        async def _(session):
            return IntentCommand(float(confidence), command)

        @wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    return decorator


def CatchRequestsException(function: Callable = None,
                           *,
                           prompt: Optional[str] = None,
                           retries: Optional[int] = None):
    """Decorator, catch exceptions from `requests` library
    
    Parameters
    ----------
    prompt : str, optional
        Prompt for error, do not prompt if empty, by default None
    retries : int, optional
        number of retries, by default 1
    
    Raises
    ------
    BotRequestError
        An exception was thrown after the robot network request was caught.
    """
    if function is None:
        return partial(CatchRequestsException, prompt=prompt, retries=retries)

    functionName = _getFunctionName(function)
    function = Timeit(function)

    @wraps(function)
    def wrapper(*args, **kwargs):
        for _ in range(retries if retries else 1):
            try:
                return function(*args, **kwargs)
            except RequestException as error:
                traceID = ExceptionProcess.catch()
                logger.debug(f'Function {functionName} encountered' +
                             f'a network request error: "{error}"')
                if isinstance(error, HTTPError):
                    break
        raise BotRequestError(prompt, traceID)

    return wrapper
