import json
import os
import time
from secrets import token_hex
from traceback import format_exc
from typing import Optional

from nonetrip.log import logger

STORE_EXCEPTION_DIR = "./data/errors"
STORE_EXCEPTION_DEPTH = 3

os.makedirs(STORE_EXCEPTION_DIR, exist_ok=True)


class BaseBotError(Exception):
    def __init__(self, reason: Optional[str] = None, trace: Optional[str] = None):
        self.reason = str(reason) if reason else None
        self.trace = str(trace).upper() if trace else None
        super().__init__(reason)


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


class ExceptionProcess:
    @staticmethod
    def _getRecursivePath(filename: str, *, makeDir: bool = False) -> str:
        name, ext = os.path.splitext(filename)
        assert len(name) >= STORE_EXCEPTION_DEPTH
        exceptionDir = os.path.join(
            STORE_EXCEPTION_DIR, *list(name[:STORE_EXCEPTION_DEPTH])
        )
        if makeDir:
            os.makedirs(exceptionDir, exist_ok=True)
        return os.path.join(exceptionDir, filename)

    @staticmethod
    def catch() -> str:
        """Catch the exception to get the exception ID

        Returns
        -------
        str
            Exception ID
        """
        trace = ExceptionProcess.store(
            exceptionTime=time.time(), exceptionStack=format_exc()
        )
        return trace.upper()

    @classmethod
    def store(cls, exceptionTime: float, exceptionStack: str) -> str:
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
        storeDir: str = cls._getRecursivePath(f"{stackID}.json", makeDir=True)
        exceptionInfo: dict = {
            "stack_id": stackID,
            "time": exceptionTime,
            "time_format": time.strftime("%c %z", time.localtime(exceptionTime)),
            "stack": exceptionStack,
        }
        with open(storeDir, "wt", encoding="utf-8") as f:
            f.write(
                json.dumps(exceptionInfo, ensure_ascii=False, indent=4, sort_keys=True)
            )
        logger.debug(
            f"Has been saved Error Stack file {storeDir}, " + f"content:{exceptionInfo}"
        )
        return stackID

    @classmethod
    def read(cls, stackID: str) -> dict:
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
        storeDir: str = cls._getRecursivePath(f"{stackID.upper()}.json")
        if not os.path.isfile(storeDir):
            raise BotNotFoundError("无法找到该追踪ID")
        with open(storeDir, "rt", encoding="utf-8") as f:
            readData = json.load(f)
        return readData
