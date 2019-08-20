from asyncio import Task, get_event_loop, get_running_loop
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial, wraps
from time import sleep, time_ns
from typing import Union

from nonebot import IntentCommand, logger, on_natural_language

_EXECUTOR = ThreadPoolExecutor()
_EVENT_LOOP = get_event_loop()


def Timeit(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        t = time_ns()
        try:
            returnData = function(*args, **kwargs)
        except:
            logger.debug(f'Function {function} cost {time_ns()-t}ns')
            raise

        logger.debug(f'Function {function} cost {time_ns()-t}ns')
        return returnData

    return wrapper


def Async(function):
    @wraps(function)
    @Timeit
    def wrapper(*args, **kwargs):
        return get_running_loop().run_in_executor\
            (_EXECUTOR, lambda: function(*args, **kwargs))

    return wrapper


def Sync(function):
    @wraps(function)
    @Timeit
    def wrapper(*args, **kwargs):
        task: Task = _EVENT_LOOP.create_task(function(*args, **kwargs))
        while not task.done():
            sleep(.1)
        if task.exception():
            raise task.exception()
        return task.result()

    return wrapper


SyncToAsync = Async
AsyncToSync = Sync


def WithKeyword(keywords: Union[str, tuple],
                command: str,
                confidence: Union[float, int] = 80.0):
    def decorator(function):
        getKeyword = keywords if type(keywords) == tuple else (keywords, )

        @on_natural_language(keywords=getKeyword)
        async def _(session):
            return IntentCommand(float(confidence), command)

        @wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    return decorator
