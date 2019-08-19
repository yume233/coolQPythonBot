from functools import partial, wraps
from time import time
from traceback import format_exc
from typing import Union

from nonebot import CommandSession, NLPSession, NoticeSession, RequestSession
from nonebot.command import SwitchException, _FinishException, _PauseException
from nonebot.session import BaseSession

from .botConfig import settings
from .customObjects import SyncWrapper
from .database import database
from .exception import *

UnionSession = Union[CommandSession, NLPSession, NoticeSession, RequestSession]


def processSession(function=None):
    @wraps(function)
    async def wrapper(session: UnionSession, *args, **kwargs):
        try:
            if not isinstance(session, BaseSession): raise BaseBotError
            await function(SyncWrapper(session), *args, **kwargs)
        except (_FinishException, _PauseException, SwitchException):
            raise
        except BotDisabledError as e:
            if not e.trace:
                e.trace = database.catchException(time(), format_exc())
            await session.send(f'已经被禁用,原因:{e.reason},追踪ID:{e.trace}')
        except BotRequestError as e:
            if not e.trace:
                e.trace = database.catchException(time(), format_exc())
            await session.send(f'请求资源失败,原因:{e.reason},追踪ID:{e.trace}')
        except BotMessageError as e:
            if not e.trace:
                e.trace = database.catchException(time(), format_exc())
            await session.send(f'信息发送失败,原因:{e.reason},追踪ID:{e.trace}')
        except BotNotFoundError as e:
            if not e.trace:
                e.trace = database.catchException(time(), format_exc())
            await session.send(f'未找到,原因:{e.reason},追踪ID:{e.trace}')
        except BotPermissionError as e:
            if not e.trace:
                e.trace = database.catchException(time(), format_exc())
            await session.send(f'您不具有权限,原因:{e.reason},追踪ID:{e.trace}')
        except BotNetworkError as e:
            if not e.trace:
                e.trace = database.catchException(time(), format_exc())
            await session.send(f'网络出错,原因:{e.reason},追踪ID:{e.trace}')
        except BotProgramError as e:
            if not e.trace:
                e.trace = database.catchException(time(), format_exc())
            await session.send(f'程序出错,原因:{e.reason},追踪ID:{e.trace}')
        except BaseBotError as e:
            if not e.trace:
                e.trace = database.catchException(time(), format_exc())
            await session.send(f'基础组件出错,原因:{e.reason},追踪ID:{e.trace}')
        except:
            if settings.DEBUG: raise
            trace = database.catchException(time(), format_exc())
            await session.send(f'出现未知错误,追踪ID:{trace},请联系开发者')

    return wrapper
