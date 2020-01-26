import json
import os
import time
from secrets import token_hex
from traceback import format_exc

from nonebot import logger

STORE_EXCEPTION_DIR = './data/errors'

if not os.path.exists(STORE_EXCEPTION_DIR):
    os.mkdir(STORE_EXCEPTION_DIR)


class BaseBotError(Exception):
    def __init__(self, reason: str = None, trace: str = None):
        """__init__ 
        
        :param reason: Cause of error, defaults to None
        :type reason: str, optional
        :param trace: The error tracking ID, defaults to None
        :type trace: str, optional
        """
        self.reason = str(reason) if reason else None
        self.trace = str(trace).upper() if trace else None
        super().__init__(reason)


class BotNetworkError(BaseBotError):
    pass


class BotProgramError(BaseBotError):
    pass


class BotNotFoundError(BotProgramError):
    pass


class BotRequestError(BotNetworkError):
    pass


class BotMessageError(BotNetworkError):
    pass


class BotPermissionError(BotProgramError):
    pass


class BotDisabledError(BotProgramError):
    pass


def CatchException() -> str:
    trace = storeExceptions(exceptionTime=time.time(),
                            exceptionStack=format_exc())
    return trace.upper()


def storeExceptions(exceptionTime: float, exceptionStack: str) -> str:
    """Store a caught exception
    
    Parameters
    ----------
    exceptionTime : float
        Timestamp when the exception occurred
    exceptionStack : str
        Exception stack
    
    Returns
    -------
    str
        Unique ID used to identify the exception
    """
    stackID: str = token_hex(4).upper()
    storeDir: str = os.path.join(STORE_EXCEPTION_DIR, f'{stackID}.json')
    exceptionInfo: dict = {
        'stack_id': stackID,
        'time': exceptionTime,
        'time_format': time.strftime('%c %z', time.localtime(exceptionTime)),
        'stack': exceptionStack
    }
    with open(storeDir, 'wt', encoding='utf-8') as f:
        f.write(
            json.dumps(exceptionInfo,
                       ensure_ascii=False,
                       indent=4,
                       sort_keys=True))
    logger.debug(f'Has been saved Error Stack file {storeDir}, ' +
                 f'content:{exceptionInfo}')
    return stackID


def readExceptions(stackID: str) -> dict:
    """Read previously caught exception
    
    Parameters
    ----------
    stackID : str
        Provided error stack ID
    
    Returns
    -------
    dict
        stack_id : Previously provided stack ID
        time : Timestamp when an error occurred
        time_format : Formatted version of the timestamp above
        stack : Exception stack
    
    Raises
    ------
    BotNotFoundError
        Throws when the exception stack for the specified ID cannot be found
    """
    storeDir: str = os.path.join(STORE_EXCEPTION_DIR,
                                 f'{stackID.upper()}.json')
    if not os.path.isfile(storeDir):
        raise BotNotFoundError('无法找到该追踪ID')
    with open(storeDir, 'rt', encoding='utf-8') as f:
        readData = json.load(f)
    return readData
