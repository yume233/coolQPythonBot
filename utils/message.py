from functools import partial, wraps
from typing import Callable, Optional, Union

from nonebot import CommandSession, NLPSession, NoticeSession, RequestSession
from nonebot.command import SwitchException, _FinishException, _PauseException
from nonebot.log import logger
from nonebot.session import BaseSession

from .botConfig import settings
from .decorators import Timeit
from .exception import (BaseBotError, BotDisabledError, BotExistError,
                        BotMessageError, BotNetworkError, BotNotFoundError,
                        BotPermissionError, BotProgramError, BotRequestError,
                        ExceptionProcess)
from .manager import PluginManager
from .objects import SyncWrapper

UnionSession = Union[CommandSession, NLPSession, NoticeSession, RequestSession]


def _messageSender(function: Callable) -> Callable:
    @wraps(function)
    async def wrapper(session: UnionSession, *args, **kwargs):
        returnData = await function(session, *args, **kwargs)
        if isinstance(returnData, tuple):
            replyData, atSender = returnData
        elif isinstance(returnData, str):
            replyData, atSender = returnData, True
        else:
            return
        if atSender: replyData = f'\n{replyData}'
        if settings.DEBUG: replyData += '\n(DEBUG)'
        await session.send(replyData, at_sender=atSender)

    return wrapper


def processSession(function: Callable = None,
                   *,
                   pluginName: Optional[str] = None,
                   convertToSync: Optional[bool] = True) -> Callable:

    if function is None:
        return partial(processSession,
                       pluginName=pluginName,
                       convertToSync=convertToSync)

    @wraps(function)
    @Timeit
    @_messageSender
    async def wrapper(session: UnionSession, *args, **kwargs):
        sessionText = ''.join([
            i['data']['text'] for i in session.ctx['message']
            if i['type'] == 'text'
        ])

        enabled = PluginManager.settings(
            pluginName=pluginName,
            ctx=session.ctx).status if pluginName else True

        if isinstance(session, CommandSession):
            for perKeyword in settings.SESSION_CANCEL_KEYWORD:
                if perKeyword in sessionText:
                    session.finish(settings.SESSION_CANCEL_EXPRESSION)

        logger.debug(f'Session Class:{type(session).__name__},' +
                     f'Plugin Name:{pluginName},' +
                     f'Message Text:"{sessionText}",' + f'Enabled:{enabled},' +
                     f'CTX:"{session.ctx}"')

        try:
            if not isinstance(session, BaseSession):
                raise BaseBotError
            if not enabled:
                if isinstance(session, CommandSession): raise BotDisabledError
                else: return
            if convertToSync:
                session = SyncWrapper(session)

            return await function(session, *args, **kwargs)

        except (_FinishException, _PauseException, SwitchException):
            raise
        except BotDisabledError as e:
            if not e.trace: e.trace = ExceptionProcess.catch()
            return f'已经被禁用,原因:{e.reason},追踪ID:{e.trace}'
        except BotRequestError as e:
            if not e.trace: e.trace = ExceptionProcess.catch()
            return f'请求资源失败,原因:{e.reason},追踪ID:{e.trace}'
        except BotMessageError as e:
            if not e.trace: e.trace = ExceptionProcess.catch()
            return f'信息发送失败,原因:{e.reason},追踪ID:{e.trace}'
        except BotNotFoundError as e:
            if not e.trace: e.trace = ExceptionProcess.catch()
            return f'未找到,原因:{e.reason},追踪ID:{e.trace}'
        except BotExistError as e:
            if not e.trace: e.trace = ExceptionProcess.catch()
            return f'已存在,原因:{e.reason},追踪ID:{e.trace}'
        except BotPermissionError as e:
            if not e.trace: e.trace = ExceptionProcess.catch()
            return f'您不具有权限,原因:{e.reason},追踪ID:{e.trace}'
        except BotNetworkError as e:
            if not e.trace: e.trace = ExceptionProcess.catch()
            return f'网络出错,原因:{e.reason},追踪ID:{e.trace}'
        except BotProgramError as e:
            if not e.trace: e.trace = ExceptionProcess.catch()
            return f'程序出错,原因:{e.reason},追踪ID:{e.trace}'
        except BaseBotError as e:
            if not e.trace: e.trace = ExceptionProcess.catch()
            return f'基础组件出错,原因:{e.reason},追踪ID:{e.trace}'
        except AssertionError as e:
            return f'程序抛出断言,原因:{e},追踪ID:{ExceptionProcess.catch()}'
        except:
            if settings.DEBUG: raise
            return f'出现未知错误,追踪ID:{ExceptionProcess.catch()},请联系开发者'

    return wrapper
