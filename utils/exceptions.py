import json
from datetime import datetime
from pathlib import Path
from secrets import token_hex
from traceback import format_exc
from typing import Optional

from pydantic import BaseModel


class ExceptionStorage:
    EXCEPTION_PATH = Path(".") / "data" / "errors"
    PATH_DEPTH = 3

    class ExceptionInfo(BaseModel):
        time: datetime
        stamp: float
        id: str
        traceback: str

    @classmethod
    def _resolvePath(cls, id_: str) -> Path:
        assert len(id_) >= cls.PATH_DEPTH
        cls.EXCEPTION_PATH.mkdir(exist_ok=True, parents=True)
        filename = id_ + ".json"
        return cls.EXCEPTION_PATH / ("/".join(filename[: cls.PATH_DEPTH])) / filename

    @classmethod
    def save(cls, traceback: str, *, time: Optional[datetime] = None) -> str:
        traceID = token_hex(8).upper()
        time = time or datetime.now()
        traceData = cls.ExceptionInfo(
            time=time, stamp=time.timestamp(), id=traceID, traceback=traceback
        )
        path = cls._resolvePath(traceID)
        path.write_text(
            json.dumps(traceData.dict(), ensure_ascii=False, indent=4, sort_keys=True),
            encoding="utf-8",
        )
        return traceID

    @classmethod
    def read(cls, id_: str):
        path = cls._resolvePath(id_.upper())
        data = path.read_text(encoding="utf-8")
        return cls.ExceptionInfo(**json.loads(data))


class BaseBotException(Exception):
    prompt: Optional[str] = None

    def __init__(self, prompt: Optional[str] = None, traceback: Optional[str] = None):
        self.prompt = prompt or self.__class__.prompt or self.__class__.__name__
        self.traceback = traceback or format_exc()
        self.traceID = ExceptionStorage.save(self.traceback)


class BotProgramException(BaseBotException):
    prompt = "程序自身故障"


class NetworkException(BotProgramException):
    prompt = "网络请求出现故障"


class QueryException(BotProgramException):
    prompt = "数据库查询故障"


class UsageIncorrectException(BaseBotException):
    prompt = "用户使用方法不正确"


class PermissionDeniedException(UsageIncorrectException):
    prompt = "使用权限不足"


class NotFoundException(UsageIncorrectException):
    prompt = "未找到相应数据"


class DataConflictException(UsageIncorrectException):
    prompt = "该数据和已有数据冲突"


class AlreadyExistsException(DataConflictException):
    prompt = "该数据已经存在"


class BadRequestException(UsageIncorrectException):
    prompt = "使用方式不正确"


class IllegalArgumentException(BadRequestException):
    prompt = "错误的使用参数"
