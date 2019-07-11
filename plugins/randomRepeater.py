from random import randint
import traceback

from nonebot import CommandSession, NLPSession, on_command, on_natural_language
from nonebot.permission import SUPERUSER, GROUP_ADMIN, check_permission, GROUP_MEMBER
from nonebot.log import logger
import json

from permission import permission

__plugin_name__ = 'randomRepeater'
RANDOM_RATE = 20
GROUP_RATE = {}


def traceTest():
    trace = traceback.extract_stack()
    traceRoute = []
    for perTrace in trace:
        traceRoute.append(tuple(perTrace))
    logger.debug(traceRoute)


@on_natural_language(only_short_message=True, permission=GROUP_MEMBER)
async def _(session: NLPSession):
    #traceTest()
    groupRate = permission.getSettings(session.ctx, __plugin_name__,
                                       {'rate': RANDOM_RATE})['rate']
    logger.debug(
        'Session CTX is:"%s"' % json.dumps(session.ctx, ensure_ascii=False))
    if not groupRate:
        return
    elif not randint(0, groupRate - 1):
        await session.send(session.msg_text)


@on_command(
    'set_repeat', aliases=('复读概率', ), permission=SUPERUSER | GROUP_ADMIN)
async def repeat(session: CommandSession):
    global RANDOM_RATE, GROUP_RATE
    if await check_permission(session.bot, session.ctx, SUPERUSER):
        RANDOM_RATE = session.get_optional('rate', RANDOM_RATE)
        sendMsg = '全局复读概率已被设置为{:.1%}'.format((
            1 / RANDOM_RATE) if RANDOM_RATE else 0)
    elif await check_permission(session.bot, session.ctx, GROUP_ADMIN):
        groupID = session.ctx.get('group_id')
        defaultValue = permission.getSettings(session.ctx, __plugin_name__,
                                              {'rate': RANDOM_RATE})['rate']
        valueGet = session.get_optional('rate', defaultValue)
        permission.applySettings(session.ctx, __plugin_name__,
                                 {'rate': valueGet})
        sendMsg = '群{group}复读概率已经被设置为{rate:.1%}'.format(
            group=groupID, rate=(1 / valueGet if valueGet else 0))
    await session.send(sendMsg)


@repeat.args_parser
async def _(session: CommandSession):
    if session.current_arg_text.strip().isdigit():
        session.state['rate'] = int(session.current_arg_text.strip())