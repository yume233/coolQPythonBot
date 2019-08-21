from functools import partial, wraps
from time import time
from traceback import format_exc
from typing import List, Union

from nonebot import (CommandSession, NLPSession, NoticeSession, RequestSession,
                     logger)
from nonebot.command import SwitchException, _FinishException, _PauseException
from nonebot.session import BaseSession

from .botConfig import settings
from .customDecorators import Timeit
from .customObjects import SyncWrapper
from .database import database
from .exception import *
from .pluginManager import manager

UnionSession = Union[CommandSession, NLPSession, NoticeSession, RequestSession]


def processSession(function=None,
                   *,
                   pluginName: str = '',
                   convToSync: bool = True):
    if function is None:
        return partial(processSession,
                       pluginName=pluginName,
                       convToSync=convToSync)

    @wraps(function)
    @Timeit
    async def wrapper(session: UnionSession, *args, **kwargs):
        returnResult = None
        sessionText = ''.join([
            i['data']['text'] for i in session.ctx['message']
            if i['type'] == 'text'
        ])

        if pluginName:
            enabled = manager.settings(pluginName, ctx=session.ctx).status
        else:
            enabled = True

        if type(session) == CommandSession:
            for perKeyword in settings.SESSION_CANCEL_KEYWORD:
                if perKeyword in sessionText:
                    session.finish(settings.SESSION_CANCEL_EXPRESSION)

        logger.debug(f'Session Class:{session},' +
                     f'Plugin Name:{pluginName},' +
                     f'Message Text:"{sessionText}",' + f'Enabled:{enabled},' +
                     f'CTX:"{session.ctx}"')

        try:
            if not isinstance(session, BaseSession): raise BaseBotError

            if not enabled:
                if type(session) == CommandSession:
                    raise BotDisabledError('此插件不允许在此处使用')
                else:
                    return

            returnResult = await function\
                (SyncWrapper(session) if convToSync else session, *args,**kwargs)

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
            if type(returnResult) == tuple:
                msg, at = returnResult
            else:
                msg, at = returnResult, True
            if at: msg = f'\n{msg}'
            await session.send(msg, at_sender=at)

    return wrapper
