from utils.database import database
from nonebot import on_command, CommandSession
from utils.customDecorators import SyncToAsync
from utils.messageProc import processSession
from nonebot.permission import SUPERUSER


@on_command('bug_catch', aliases=('追踪', '跟踪'), permission=SUPERUSER)
@processSession
@SyncToAsync
def catch(session: CommandSession):
    id = session.get('id')
    data = database.getException(id)
    returnData = '''
    追踪ID:{trace_id}
    错误编码:{error_id}
    出错时间戳:{time}
    错误堆栈:\n{stack}'''.format(**data)
    return returnData


@catch.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('请输入错误追踪ID')
    session.state['id'] = strippedArgs