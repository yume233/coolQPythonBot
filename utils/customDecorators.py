from asyncio import Task, get_event_loop, set_event_loop
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial, wraps
from time import sleep, time
from typing import Union

from nonebot import IntentCommand, logger, on_natural_language
from requests import HTTPError, RequestException

from .botConfig import settings
from .exception import BotRequestError, CatchException

_EXECUTOR = ThreadPoolExecutor(settings.THREAD_POOL_NUM)
_EVENT_LOOP = get_event_loop()


def Timeit(function):
    """Decorator for timing a function
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        t = time() * 1000
        try:
            returnData = function(*args, **kwargs)
        except:
            logger.debug(f'Function {function} cost {time()*1000-t}ms')
            raise

        logger.debug(f'Function {function} cost {time()*1000-t}ms')
        return returnData

    return wrapper


def SyncToAsync(function):
    """Decorator to convert synchronous functions to asynchronous functions
    """    
    @wraps(function)
    def wrapper(*args, **kwargs):
        @Timeit
        def runner():
            set_event_loop(_EVENT_LOOP)
            return function(*args, **kwargs)

        return _EVENT_LOOP.run_in_executor(_EXECUTOR, runner)

    return wrapper


def AsyncToSync(function):
    """Decorator to convert asynchronous functions to synchronous functions
    """    
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


Async = SyncToAsync
Sync = AsyncToSync


def WithKeyword(keywords: Union[str, tuple],
                command: str,
                confidence: Union[float, int] = 80.0):
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


def CatchRequestsException(function=None,
                           *,
                           prompt: str = None,
                           retries: int = 1):
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

    @wraps(function)
    @Timeit
    def wrapper(*args, **kwargs):
        for _ in range(retries):
            try:
                return function(*args, **kwargs)
            except RequestException as error:
                traceID = CatchException()
                logger.debug(
                    f'Request Function {function} Error Occured:{error}')
        raise BotRequestError(prompt, traceID)

    return wrapper
