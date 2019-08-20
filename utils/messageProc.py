from functools import partial, wraps
from time import time
from traceback import format_exc
from typing import List, Union

from nonebot import (CommandSession, NLPSession, NoticeSession, RequestSession,
                     logger)
from nonebot.command import SwitchException, _FinishException, _PauseException
from nonebot.session import BaseSession

from .botConfig import settings
from .customObjects import SyncWrapper
from .database import database
from .exception import *
from .pluginManager import manager

UnionSession = Union[CommandSession, NLPSession, NoticeSession, RequestSession]


def nameJoin(pluginName: str, *methodsName) -> str:
    def cleanDot(name: str) -> str:
        if name.startswith('.'):
            name = name[1:]
        if name.endswith('.'):
            name = name[:-1]
        return name

    methodsName: List[str] = [cleanDot(i) for i in methodsName if i]
    methodsName.insert(0, cleanDot(pluginName))
    return '.'.join(methodsName)


def processSession(function=None,
                   *,
                   pluginName: str = None,
                   methodName: str = None):
    if function is None:
        return partial(processSession,
                       pluginName=pluginName,
                       methodName=methodName)

    @wraps(function)
    async def wrapper(session: UnionSession, *args, **kwargs):
        sessionText = ''.join([
            i['data']['text'] for i in session.ctx['message']
            if i['type'] == 'text'
        ])

        if (pluginName and methodName):
            fullPluginName = nameJoin(pluginName, *methodName.split('.'))
            chatType = 'group' if session.ctx.get('group_id') else 'user'
            getID = session.ctx.get('group_id', session.ctx['user_id'])
            enabled = manager.settings(fullPluginName, getID, chatType).status
        else:
            fullPluginName = None
            enabled = True

        logger.debug(f'Session Class:{session},' +
                     f'Plugin Name:{fullPluginName}' +
                     f'Message Text:"{sessionText}",' + f'Enabled:{enabled},' +
                     f'CTX:"{session.ctx}"')

        try:
            if not isinstance(session, BaseSession): raise BaseBotError
            if not enabled: raise BotDisabledError('此插件不允许在此处使用')
            getText = await function(SyncWrapper(session), *args, **kwargs)
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
        except AssertionError as e:
            trace = database.catchException(time(), format_exc())
            await session.send(f'程序抛出断言,原因:{e},追踪ID:{trace}')
        except:
            if settings.DEBUG: raise
            trace = database.catchException(time(), format_exc())
            await session.send(f'出现未知错误,追踪ID:{trace},请联系开发者')
        if getText: await session.send(getText, at_sender=True)
        session.finish()

    return wrapper
