from asyncio import AbstractEventLoop, get_event_loop
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial, wraps

EXECUTOR = ThreadPoolExecutor()


def Async(function=None, *, loop: AbstractEventLoop = get_event_loop()):
    if function is None:
        return partial(Async, loop=loop)

    @wraps(function)
    def wrapper(*args, **kwargs):
        return loop.run_in_executor(EXECUTOR,
                                    lambda: function(*args, **kwargs))

    return wrapper


def Sync(function=None, *, loop: AbstractEventLoop = get_event_loop()):
    if function is None:
        return partial(Sync, loop=loop)

    @wraps(function)
    def wrapper(*args, **kwargs):
        return loop.run_until_complete(function(*args, **kwargs))

    return wrapper
