from functools import partial, wraps
from re import compile as compileRegexp
from typing import Callable, Optional, Tuple, Union

from nonetrip import CommandSession, NLPSession, NoneBot, NoticeSession, RequestSession
from nonetrip.command import (
    SwitchException,
    ValidateError,
    _FinishException,
    _PauseException,
)
from nonetrip.command.argfilter.controllers import handle_cancellation
from nonetrip.command.argfilter.extractors import extract_text
from nonetrip.compat import Event
from nonetrip.log import logger
from nonetrip.message import CanceledException, MessageSegment, message_preprocessor
from nonetrip.session import BaseSession

from .botConfig import settings
from .decorators import Timeit
from .exception import (
    BaseBotError,
    BotDisabledError,
    BotExistError,
    BotMessageError,
    BotNetworkError,
    BotNotFoundError,
    BotPermissionError,
    BotProgramError,
    BotRequestError,
    ExceptionProcess,
)
from .manager import PluginManager
from .objects import SyncWrapper

UnionSession = Union[CommandSession, NLPSession, NoticeSession, RequestSession]
CQ_CODE = compileRegexp(r"\[(CQ:\w+)(?:,\w+=[^,]+)*\]")


@message_preprocessor
async def _(bot: NoneBot, event: Event, plugin_manager):
    loginInfo = await bot.get_login_info()

    if loginInfo["user_id"] != event.self_id:
        raise CanceledException(None)

    return


def _shortCQCode(message: str) -> str:
    return CQ_CODE.sub(r"[\1...]", message).__repr__()


def _messageSender(function: Callable) -> Callable:
    @wraps(function)
    async def wrapper(session: UnionSession, *args, **kwargs):
        returnData: Union[Tuple[str, bool], str] = await function(
            session, *args, **kwargs
        )
        if isinstance(returnData, tuple):
            replyData, atSender = returnData
        else:
            replyData, atSender = returnData, True

        if not isinstance(replyData, (str, MessageSegment)):
            return

        replyData = str(replyData)

        if atSender:
            replyData = "\n" + replyData
        if settings.DEBUG:
            replyData += "\n(DEBUG)"
        logger.info(
            "Reply to message of conversation "
            + f'{session.ctx["message_id"]} as {_shortCQCode(replyData)}'
        )

        if hasattr(session, "finish"):
            session.finish(replyData, at_sender=atSender)
        else:
            await session.send(replyData, at_sender=atSender)

    return wrapper


def processSession(
    function: Callable = None,
    *,
    pluginName: Optional[str] = None,
    convertToSync: Optional[bool] = True,
) -> Callable:

    if function is None:
        return partial(
            processSession, pluginName=pluginName, convertToSync=convertToSync
        )

    @wraps(function)
    @Timeit
    @_messageSender
    async def wrapper(session: UnionSession, *args, **kwargs):
        assert isinstance(session, BaseSession)
        sessionType = type(session)

        sessionMessage: str = extract_text(session.ctx["message"])

        enabled = (
            PluginManager.settings(pluginName=pluginName, ctx=session.ctx).status
            if pluginName
            else True
        )

        logger.debug(
            "Session information:"
            + ",".join(
                [
                    f"type={sessionType.__name__}",
                    f"plugin={pluginName}",
                    f"content={sessionMessage.__repr__()}",
                    f"ctx={session.ctx}",
                    f"enabled={enabled}",
                ]
            )
        )

        if isinstance(session, CommandSession):
            cancelController = handle_cancellation(session)
            cancelController(sessionMessage)

        try:
            if not enabled:
                if isinstance(session, CommandSession):
                    raise BotDisabledError
                else:
                    return
            execSession = SyncWrapper(session) if convertToSync else session
            return await function(execSession, *args, **kwargs)

        except (_FinishException, _PauseException, SwitchException, ValidateError):
            raise
        except BotDisabledError as e:
            if not e.trace:
                e.trace = ExceptionProcess.catch()
            return f"已经被禁用,原因:{e.reason},追踪ID:{e.trace}"
        except BotRequestError as e:
            if not e.trace:
                e.trace = ExceptionProcess.catch()
            return f"请求资源失败,原因:{e.reason},追踪ID:{e.trace}"
        except BotMessageError as e:
            if not e.trace:
                e.trace = ExceptionProcess.catch()
            return f"信息发送失败,原因:{e.reason},追踪ID:{e.trace}"
        except BotNotFoundError as e:
            if not e.trace:
                e.trace = ExceptionProcess.catch()
            return f"未找到,原因:{e.reason},追踪ID:{e.trace}"
        except BotExistError as e:
            if not e.trace:
                e.trace = ExceptionProcess.catch()
            return f"已存在,原因:{e.reason},追踪ID:{e.trace}"
        except BotPermissionError as e:
            if not e.trace:
                e.trace = ExceptionProcess.catch()
            return f"您不具有权限,原因:{e.reason},追踪ID:{e.trace}"
        except BotNetworkError as e:
            if not e.trace:
                e.trace = ExceptionProcess.catch()
            return f"网络出错,原因:{e.reason},追踪ID:{e.trace}"
        except BotProgramError as e:
            if not e.trace:
                e.trace = ExceptionProcess.catch()
            return f"程序出错,原因:{e.reason},追踪ID:{e.trace}"
        except BaseBotError as e:
            if not e.trace:
                e.trace = ExceptionProcess.catch()
            return f"基础组件出错,原因:{e.reason},追踪ID:{e.trace}"
        except AssertionError as e:
            return f"程序抛出断言,原因:{e},追踪ID:{ExceptionProcess.catch()}"
        except Exception:
            from loguru import logger as loguruLogger

            traceID = ExceptionProcess.catch()
            loguruLogger.exception(
                f"An unknown error (ID:{traceID}) occurred while"
                + f'processing message {session.ctx["message_id"]}:'
            )

            if not sessionType == CommandSession:
                return
            return f"出现未知错误,追踪ID:{traceID},请联系开发者"

    return wrapper
