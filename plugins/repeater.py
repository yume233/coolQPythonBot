from random import randint

from nonetrip import CommandSession, NLPSession, logger, on_command, on_natural_language
from nonetrip.permission import GROUP_ADMIN, GROUP_MEMBER, SUPERUSER
from utils.decorators import SyncToAsync
from utils.manager import PluginManager
from utils.message import processSession
from utils.objects import SyncWrapper

__plugin_name__ = "repeater"

PluginManager.registerPlugin(
    __plugin_name__, defaultStatus=True, defaultSettings={"rate": 20}
)


@on_natural_language(permission=GROUP_MEMBER, only_to_me=False)
@processSession(pluginName=__plugin_name__)
@SyncToAsync
def _(session: NLPSession):
    groupRate = PluginManager.settings(__plugin_name__, ctx=session.ctx).settings[
        "rate"
    ]
    randomNum, msgID = randint(0, groupRate - 1), session.ctx["message_id"]
    groupID = session.ctx.get("group_id")
    if not groupID:
        return
    logger.debug(
        f"Chat {groupID} has a repeat probability of {1/groupRate:.3%}."
        + f"The random number of the current session {msgID} is {randomNum}."
    )
    if not randomNum:
        return session.msg, False


@on_command("repeat_rate", aliases=("复读概率",), permission=SUPERUSER | GROUP_ADMIN)
@processSession
@SyncToAsync
def repeatSetter(session: CommandSession):
    getSettings = PluginManager.settings(__plugin_name__, ctx=session.ctx)
    getRate = session.get_optional("rate", False)
    getRate = getRate if getRate else getSettings.settings["rate"]
    groupID = session.ctx["group_id"]
    if not getSettings.status:
        getSettings.status = True
    getSettings.settings = {"rate": getRate}
    return f"群{groupID}复读概率已被设置为{1/getRate:.3%}"


@repeatSetter.args_parser
@processSession
@SyncToAsync
def _(session: CommandSession):
    if session.current_arg_text.strip().isdigit():
        rate = int(session.current_arg_text.strip())
        if rate <= 0:
            session.finish("无效的复读概率值,应为一个正整数")
        session.state["rate"] = rate


@on_command("repeat_disable", aliases=("关闭复读",), permission=SUPERUSER | GROUP_ADMIN)
@SyncToAsync
def _(session: CommandSession):
    session: CommandSession = SyncWrapper(session)
    groupID = session.ctx["group_id"]
    getSettings = PluginManager.settings(__plugin_name__, ctx=session.ctx)
    getSettings.status = False
    session.send(f"群{groupID}复读已经关闭")
