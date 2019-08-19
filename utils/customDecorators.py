from asyncio import get_running_loop
from asyncio import run as asyncRun
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial, wraps

EXECUTOR = ThreadPoolExecutor()


def Async(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return get_running_loop().run_in_executor(
            EXECUTOR, lambda: function(*args, **kwargs))

    return wrapper


def Sync(function=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return asyncRun(function(*args, **kwargs))

    return wrapper
