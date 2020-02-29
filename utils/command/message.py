from asyncio import create_task, iscoroutinefunction
from asyncio import sleep as asyncSleep
from functools import partial, wraps
from typing import Any, Callable, Dict, Optional, Tuple, Union

from nonebot import get_bot, scheduler
from nonebot.command import (CommandHandler_T, CommandName_T, CommandSession,
                             SwitchException, ValidateError, _FinishException,
                             _PauseException, on_command)
from nonebot.command.argfilter.controllers import handle_cancellation
from nonebot.command.argfilter.extractors import extract_text
from nonebot.permission import check_permission

from ..exceptions import (BaseBotError, BotDisabledError, BotExistError,
                          BotMessageError, BotNetworkError, BotNotFoundError,
                          BotPermissionError, BotProgramError,
                          BotRateLimitError, BotRequestError, ExceptionProcess)
from ..log import logger
from ..objects.classes import SyncWrapper
from ..objects.decorators import SyncToAsync, Timing
from ..settings.bot import settings as botSettings
from .settings import CommandSettings, SettingLocation_T, SingleSetting

_SETTINGS: Dict[int, SingleSetting] = {}
_CALL_RATE: Dict[SettingLocation_T, Dict[CommandName_T, int]] = {}


@scheduler.scheduled_job('interval', minutes=1)
async def _():
    global _CALL_RATE
    _CALL_RATE.clear()


def _messageSender(function: Callable) -> Callable:
    @wraps(function)
    async def wrapper(session: CommandSession, *args, **kwargs):
        global _SETTINGS
        returnData: Optional[Union[Tuple[str, bool], str]]
        returnData = await function(session, *args, **kwargs)
        setting = _SETTINGS.pop(session.ctx['message_id'])

        if isinstance(returnData, tuple):
            replyData, atSender = returnData
        elif isinstance(returnData, str):
            replyData, atSender = returnData, True
        else:
            return

        if atSender: replyData = '\n' + replyData
        if botSettings.DEBUG: replyData += '\n(DEBUG)'
        logger.info(
            'Reply to message of conversation ' +
            f'{session.ctx["message_id"]} as {replyData.__repr__():.100s}')

        msgID = await session.send(replyData, at_sender=atSender)
        if setting.autoDelete:

            async def _remover():
                await asyncSleep(60)
                await get_bot().delete_msg(message_id=msgID)

            session.bot.loop.create_task(_remover(), name=f'Remover-{msgID}')
        session.finish()

    return wrapper


@_messageSender
async def _funcRunner(session: CommandSession, function: CommandHandler_T,
                      name: CommandName_T) -> str:
    global _SETTINGS, _CALL_RATE
    assert isinstance(session, CommandSession)

    setting = CommandSettings(name, session.ctx).data
    sessionMessage: str = extract_text(session.ctx['message'])
    permitted = check_permission(
        session.bot,
        session.ctx,
        setting.permission,
    )
    _SETTINGS[session.ctx['message_id']] = setting

    location = setting.location
    _CALL_RATE.setdefault(location, {})
    if name in _CALL_RATE[location]:
        _CALL_RATE[location][name] += 1
    else:
        _CALL_RATE[location][name] = 0

    logger.debug(
        'Session information:' + ','.join([
            f'command={name}',
            f'content={sessionMessage.__repr__()}',
            f'ctx={session.ctx}',
            f'enabled={setting.enabled}',
            f'permitted={permitted}',
            f'rate={_CALL_RATE[location][name]}',
        ], ), )

    handle_cancellation(session)(sessionMessage)

    if not iscoroutinefunction(function):
        session = SyncWrapper(session)
        function = SyncToAsync(function)

    try:
        if not setting.enabled:
            raise BotDisabledError
        if _CALLERS[location][name] >= setting.freqency:
            raise BotRateLimitError
        if not permitted:
            raise BotPermissionError

        return await function(session)

    except (_FinishException, _PauseException, SwitchException, ValidateError):
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
    except BotRateLimitError as e:
        if not e.trace: e.trace = ExceptionProcess.catch()
        return f'调用超限,原因:{e.reason},追踪ID:{e.trace}'
    except BotProgramError as e:
        if not e.trace: e.trace = ExceptionProcess.catch()
        return f'程序出错,原因:{e.reason},追踪ID:{e.trace}'
    except BaseBotError as e:
        if not e.trace: e.trace = ExceptionProcess.catch()
        return f'基础组件出错,原因:{e.reason},追踪ID:{e.trace}'
    except AssertionError as e:
        return f'程序抛出断言,原因:{e},追踪ID:{ExceptionProcess.catch()}'
    except:
        traceID = ExceptionProcess.catch()
        logger.exception(f'An unknown error (ID:{traceID}) occurred while' +
                         f'processing message {session.ctx["message_id"]}:')
        return f'出现未知错误,追踪ID:{traceID},请联系开发者'


class CommandFunction:
    def __init__(self, function: CommandHandler_T, name: CommandName_T,
                 **kwargs):
        self.__call__ = partial(_funcRunner, function=function, name=name)
        self._name = name
        self._exec = on_command(name, **kwargs)(self.__call__)

    def args_parser(self, function: CommandHandler_T) -> CommandHandler_T:
        runner = partial(_funcRunner, function=function, name=self._name)
        return self._exec.args_parser(runner)
