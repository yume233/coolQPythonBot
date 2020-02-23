import json
import os
import time
from secrets import token_hex
from traceback import format_exc
from typing import Optional

from .log import logger

STORE_EXCEPTION_DIR = './data/errors'

if not os.path.exists(STORE_EXCEPTION_DIR):
    os.mkdir(STORE_EXCEPTION_DIR)


class ExceptionProcess:
    @staticmethod
    def catch() -> str:
        trace = ExceptionProcess.store(exceptionTime=time.time(),
                                       exceptionStack=format_exc())
        return trace.upper()

    @staticmethod
    def store(exceptionTime: float, exceptionStack: str) -> str:
        stackID: str = token_hex(4).upper()
        storeDir: str = os.path.join(STORE_EXCEPTION_DIR, f'{stackID}.json')
        exceptionInfo: dict = {
            'stack_id': stackID,
            'time': exceptionTime,
            'time_format': time.strftime('%c %z',
                                         time.localtime(exceptionTime)),
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

    @staticmethod
    def read(stackID: str) -> dict:
        storeDir: str = os.path.join(STORE_EXCEPTION_DIR,
                                     f'{stackID.upper()}.json')
        if not os.path.isfile(storeDir):
            raise BotNotFoundError('无法找到该追踪ID')
        with open(storeDir, 'rt', encoding='utf-8') as f:
            readData = json.load(f)
        return readData


class BaseBotError(Exception):
    def __init__(self,
                 reason: Optional[str] = None,
                 trace: Optional[str] = None):
        super().__init__(reason)
        self.reason = str(reason) if reason else None
        self.trace = str(trace).upper() if trace else None


class BotNetworkError(BaseBotError):
    pass


class BotProgramError(BaseBotError):
    pass


class BotNotFoundError(BotProgramError):
    pass


class BotExistError(BotProgramError):
    pass


class BotPermissionError(BotProgramError):
    pass


class BotDisabledError(BotProgramError):
    pass


class BotRequestError(BotNetworkError):
    pass


class BotMessageError(BotNetworkError):
    pass
