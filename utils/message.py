from functools import partial, wraps
from time import time
from traceback import format_exc
from typing import List, Union

from nonebot import (CommandSession, NLPSession, NoticeSession, RequestSession,
                     logger)
from nonebot.command import SwitchException, _FinishException, _PauseException
from nonebot.session import BaseSession

from .botConfig import settings
from .database import database
from .decorators import Timeit
from .exception import *
from .manager import PluginManager
from .objects import SyncWrapper

UnionSession = Union[CommandSession, NLPSession, NoticeSession, RequestSession]


def processSession(function: callable = None,
                   *,
                   pluginName: str = '',
                   convertToSync: bool = True):

    if function is None:
        return partial(processSession,
                       pluginName=pluginName,
                       convertToSync=convertToSync)

    @wraps(function)
    @Timeit
    async def wrapper(session: UnionSession, *args, **kwargs):
        returnResult = None
        sessionText = ''.join([
            i['data']['text'] for i in session.ctx['message']
            if i['type'] == 'text'
        ])

        enabled = PluginManager.settings\
            (pluginName, ctx=session.ctx).status if pluginName else True

        if not enabled:
            if type(session) == CommandSession:
                session.finish('此插件已经被禁用')
            else:
                return

        if isinstance(session, CommandSession):
            for perKeyword in settings.SESSION_CANCEL_KEYWORD:
                if perKeyword in sessionText:
                    session.finish(settings.SESSION_CANCEL_EXPRESSION)

        logger.debug(f'Session Class:{session},' +
                     f'Plugin Name:{pluginName},' +
                     f'Message Text:"{sessionText}",' + f'Enabled:{enabled},' +
                     f'CTX:"{session.ctx}"')

        try:
            if not isinstance(session, BaseSession):
                raise BaseBotError
            if not enabled and isinstance(session, CommandSession):
                raise BotDisabledError

            returnResult = await function\
                (SyncWrapper(session) if convertToSync else session, *args,**kwargs)

        except (_FinishException, _PauseException, SwitchException):
            raise
        except BotDisabledError as e:
            if not e.trace: e.trace = CatchException()
            await session.send(f'已经被禁用,原因:{e.reason},追踪ID:{e.trace}')
        except BotRequestError as e:
            if not e.trace: e.trace = CatchException()
            await session.send(f'请求资源失败,原因:{e.reason},追踪ID:{e.trace}')
        except BotMessageError as e:
            if not e.trace: e.trace = CatchException()
            await session.send(f'信息发送失败,原因:{e.reason},追踪ID:{e.trace}')
        except BotNotFoundError as e:
            if not e.trace: e.trace = CatchException()
            await session.send(f'未找到,原因:{e.reason},追踪ID:{e.trace}')
        except BotPermissionError as e:
            if not e.trace: e.trace = CatchException()
            await session.send(f'您不具有权限,原因:{e.reason},追踪ID:{e.trace}')
        except BotNetworkError as e:
            if not e.trace: e.trace = CatchException()
            await session.send(f'网络出错,原因:{e.reason},追踪ID:{e.trace}')
        except BotProgramError as e:
            if not e.trace: e.trace = CatchException()
            await session.send(f'程序出错,原因:{e.reason},追踪ID:{e.trace}')
        except BaseBotError as e:
            if not e.trace: e.trace = CatchException()
            await session.send(f'基础组件出错,原因:{e.reason},追踪ID:{e.trace}')
        except AssertionError as e:
            await session.send(f'程序抛出断言,原因:{e},追踪ID:{CatchException()}')
        except:
            if settings.DEBUG: raise
            await session.send(f'出现未知错误,追踪ID:{CatchException()},请联系开发者')

        if returnResult:
            msg,at = returnResult if \
                isinstance(returnResult,tuple) else (returnResult,True)
            msg = f'\n{msg}' if at else msg
            msg += '\n(DEBUG)' if settings.DEBUG else ''

            await session.send(msg, at_sender=at)

    return wrapper
