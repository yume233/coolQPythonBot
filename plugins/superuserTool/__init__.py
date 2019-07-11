from nonebot import on_command, CommandSession, get_bot, NoneBot
from nonebot.permission import SUPERUSER
from .managerTool import broadcast


@on_command('broadcast', aliases=('广播', ), permission=SUPERUSER)
async def broadcastFunc(session: CommandSession):
    broadcastMsg = session.get('msg')
    testGroups = session.get_optional('test', default=None)
    if not testGroups:
        await broadcast(broadcastMsg)
    else:
        await broadcast(broadcastMsg, test=[testGroups])


@broadcastFunc.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg.strip()
    if '-' in session.current_arg_text:
        session.finish('广播进程提前结束')
    if not strippedArgs:
        session.pause('请输入你要广播的内容')
    if 'test' in session.current_arg_text:
        _, testGroup = session.current_arg_text.split(' ', 1)
        session.state['test'] = int(testGroup)
    session.state['msg'] = strippedArgs