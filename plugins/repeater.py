from random import randint

from nonebot import (CommandSession, NLPSession, logger, on_command,
                     on_natural_language)
from nonebot.permission import GROUP_ADMIN, GROUP_MEMBER, SUPERUSER

from utils.customDecorators import SyncToAsync
from utils.customObjects import SyncWrapper
from utils.messageProc import processSession
from utils.pluginManager import manager

manager.registerPlugin('repeater',
                       defaultStatus=True,
                       defaultSettings={'rate': 20})


@on_natural_language(only_short_message=True, permission=GROUP_MEMBER)
@processSession(pluginName='repeater')
@SyncToAsync
def _(session: NLPSession):
    groupRate = manager.settings('repeater', ctx=session.ctx).settings['rate']
    randomNum, msgID = randint(0, groupRate - 1), session.ctx['message_id']
    sessID = session.ctx.get('group_id')
    if not sessID:
        return
    logger.debug(f'Repeat Rate of Group {sessID} is {(1/groupRate)*100}%,' +
                 f'Now Random Number of message {msgID} is {randomNum}')
    if not randomNum:
        return session.msg, False


@on_command('repeat_rate',
            aliases=('复读概率', ),
            permission=SUPERUSER | GROUP_ADMIN)
@processSession
@SyncToAsync
def repeatSetter(session: CommandSession):
    getRate = session.get_optional('rate', 20)
    sessID = session.ctx['group_id']
    getSettings = manager.settings('repeater', ctx=session.ctx)
    if not getSettings.status: getSettings.status = True
    getSettings.settings = {'rate': getRate}
    session.send(f'群{sessID}复读概率已被设置为{(1/getRate)*100}%')


@repeatSetter.args_parser
@processSession
@SyncToAsync
def _(session: CommandSession):
    if session.current_arg_text.strip().isdigit():
        rate = int(session.current_arg_text.strip())
        if rate <= 0:
            session.finish('无效的复读概率值,应为一个有效的正整数')
        session.state['rate'] = rate


@on_command('repeat_disable',
            aliases=('关闭复读', ),
            permission=SUPERUSER | GROUP_ADMIN)
@SyncToAsync
def _(session: CommandSession):
    session: CommandSession = SyncWrapper(session)
    sessID = session.ctx['group_id']
    getSettings = manager.settings('repeater', ctx=session.ctx)
    getSettings.status = False
    session.send(f'群{sessID}复读已经关闭')
