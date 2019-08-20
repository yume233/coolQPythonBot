from random import randint

from nonebot import CommandSession, NLPSession, on_command, on_natural_language
from nonebot.permission import GROUP_ADMIN, GROUP_MEMBER, SUPERUSER

from utils.customDecorators import SyncToAsync
from utils.customObjects import SyncWrapper
from utils.messageProc import processSession
from utils.pluginManager import manager

manager.registerPlugin('repeater',
                       defaultStatus=False,
                       defaultSettings={'rate': 20})


@on_natural_language(only_short_message=True, permission=GROUP_MEMBER)
@processSession(pluginName='repeater')
@SyncToAsync
def _(session: NLPSession):
    sessType = session.ctx['message_type'] \
        if session.ctx['message_type'] == 'group' else 'user'
    sessID = session.ctx['group_id'] \
        if sessType == 'group' else session.ctx['user_id']
    groupRate = manager.settings('repeater', sessID, sessType).settings['rate']
    if not randint(0, groupRate - 1):
        return session.msg, False


@on_command('repeat_rate',
            aliases=('复读概率', ),
            permission=SUPERUSER | GROUP_ADMIN)
@SyncToAsync
def repeatSetter(session: CommandSession):
    getRate = session.get_optional('rate', 20)
    session: CommandSession = SyncWrapper(session)
    sessType = session.ctx['message_type'] \
        if session.ctx['message_type'] == 'group' else 'user'
    sessID = session.ctx['group_id'] \
        if sessType == 'group' else session.ctx['user_id']
    getSettings = manager.settings('repeater', sessID, sessType)
    if not getSettings.status: getSettings.status = True
    getSettings.settings = {'rate': getRate}
    session.send(f'群{sessID}复读概率已被设置为{(1/getRate)*100}%')


@repeatSetter.args_parser
async def _(session: CommandSession):
    if session.current_arg_text.strip().isdigit():
        rate = int(session.current_arg_text.strip())
        if not rate:
            session.finish('无效的复读概率值,应为一个有效的正整数')
        session.state['rate'] = rate


@on_command('repeat_disable',
            aliases=('关闭复读', ),
            permission=SUPERUSER | GROUP_ADMIN)
@SyncToAsync
def _(session: CommandSession):
    session: CommandSession = SyncWrapper(session)
    sessType = session.ctx['message_type'] \
        if session.ctx['message_type'] == 'group' else 'user'
    sessID = session.ctx['group_id'] \
        if sessType == 'group' else session.ctx['user_id']
    getSettings = manager.settings('repeater', sessID, sessType)
    getSettings.status = False
    session.send(f'群{sessID}复读已经关闭')
