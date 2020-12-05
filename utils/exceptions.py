import json
from datetime import datetime
from pathlib import Path
from secrets import token_hex
from traceback import format_exc
from typing import Optional

import aiofiles
from nonebot.message import run_postprocessor
from nonebot.typing import Bot, Event, Matcher
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
        filename = id_ + ".json"
        path = cls.EXCEPTION_PATH / ("/".join(filename[: cls.PATH_DEPTH])) / filename
        path.parent.mkdir(exist_ok=True, parents=True)
        return path

    @classmethod
    async def save(cls, traceback: str, *, time: Optional[datetime] = None) -> str:
        traceID = token_hex(8).upper()
        time = time or datetime.now()
        traceData = cls.ExceptionInfo(
            time=time, stamp=time.timestamp(), id=traceID, traceback=traceback
        )
        path = cls._resolvePath(traceID)
        async with aiofiles.open(path, "wt", encoding="utf-8") as target:  # type:ignore
            await target.write(
                json.dumps(
                    traceData.dict(), ensure_ascii=False, indent=4, sort_keys=True
                )
            )
        return traceID

    @classmethod
    async def read(cls, id_: str):
        path = cls._resolvePath(id_.upper())
        async with aiofiles.open(path, "rt", encoding="utf-8") as target:  # type:ignore
            data = await target.read()
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


@run_postprocessor
async def _storeException(
    matcher: Matcher,
    exception: Optional[Exception],
    bot: Bot,
    event: Event,
    state: dict,
):
    reason, trace = "", ""
    if exception is None:
        return
    try:
        raise exception
    except BaseBotException as e:
        reason, trace = e.prompt, e.traceID  # type:ignore
    except Exception as e:
        reason, trace = (
            "未知故障:" + e.__class__.__name__,
            await ExceptionStorage.save(format_exc()),
        )
    await bot.send(event, message=f"出现问题\n信息:{reason}\n追寻ID:{trace}")
