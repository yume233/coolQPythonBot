from nonebot import CommandSession, on_command
from nonebot.permission import SUPERUSER

from utils.exception import readExceptions
from utils.decorators import SyncToAsync
from utils.message import processSession


@on_command('bug_catch', aliases=('追踪', '跟踪'), permission=SUPERUSER)
@processSession
@SyncToAsync
def catch(session: CommandSession):
    stackID: str = session.get('id')
    returnData = '''
    追踪ID:{stack_id}
    出错时间:{time_format}(时间戳{time})
    错误堆栈:\n{stack}'''.format(**readExceptions(stackID.upper()))
    return returnData


@catch.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('请输入错误追踪ID')
    session.state['id'] = strippedArgs
