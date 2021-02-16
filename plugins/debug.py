from nonetrip import CommandSession, on_command
from nonetrip.permission import SUPERUSER
from utils.decorators import SyncToAsync, WithKeyword
from utils.exception import ExceptionProcess
from utils.message import processSession


@on_command("bug_catch", aliases=("追踪", "跟踪"), permission=SUPERUSER)
@processSession
@SyncToAsync
def catch(session: CommandSession):
    stackID: str = session.get("id")
    returnData = """
    追踪ID:{stack_id}
    出错时间:{time_format}(时间戳{time})
    错误堆栈:\n{stack}""".format(
        **ExceptionProcess.read(stackID.upper())
    )
    return returnData


@catch.args_parser
@SyncToAsync
def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause("请输入错误追踪ID")
    session.state["id"] = strippedArgs


@on_command("ping", aliases=("在线状态",))
@WithKeyword(("在？", "在?"), "ping", confidence=100)
@processSession
@SyncToAsync
def _(session: CommandSession):
    return "你好,在的", False
