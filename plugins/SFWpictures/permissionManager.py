from nonebot import CommandSession, on_command
from nonebot.permission import GROUP_ADMIN, SUPERUSER

from permission import permission
__plugin_name__ = 'SFWPictures'


@on_command('set_setu_disable_rank', permission=SUPERUSER | GROUP_ADMIN)
async def setRank(session: CommandSession):
    groupNotAvalRank = list(set(session.get('aval')))
    permission.applySettings(session.ctx, __plugin_name__,
                             {'aval': groupNotAvalRank})
    await session.send('本群将对普通群员关闭%s等级涩图' % ','.join(groupNotAvalRank))


@setRank.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.finish('未输入要禁用的涩图等级')
    for perRank in list(strippedArgs):
        if not perRank.upper() in list('QSE'):
            session.finish('%s评级涩图不存在' % perRank)
    session.state['aval'] = strippedArgs.upper()


@on_command('disable_setu', permission=SUPERUSER | GROUP_ADMIN)
async def _(session: CommandSession):
    permission.disablePlugin(session.ctx, __plugin_name__)
    await session.send('涩图功能已禁用')


@on_command('enable_setu', permission=SUPERUSER | GROUP_ADMIN)
async def _(session: CommandSession):
    permission.enablePlugin(session.ctx, __plugin_name__)
    await session.send('涩图功能已启用')
