from re import compile as compileRegexp

from nonetrip import (
    CommandSession,
    IntentCommand,
    NLPSession,
    on_command,
    on_natural_language,
)
from nonetrip.permission import GROUP_ADMIN, SUPERUSER
from utils.decorators import SyncToAsync
from utils.manager import PluginManager
from utils.message import processSession

from .config import CONFIG
from .parse import BiliParser, IDCoverter, getVideoInfo

REPLY_FORMAT = CONFIG.customize.video
POWER_GROUP = SUPERUSER | GROUP_ADMIN
MATCH_AV = compileRegexp(CONFIG.customize.regexp.av)
MATCH_BV = compileRegexp(CONFIG.customize.regexp.bv)

__plugin_name__ = "bilibili"

PluginManager(__plugin_name__)


@on_command("bilibili_info", aliases=("视频信息", "b站视频"))
@processSession(pluginName=__plugin_name__)
@SyncToAsync
def vidInfo(session: CommandSession):
    aid = session.state["id"]
    responseData = getVideoInfo(aid)
    try:
        parsedData = BiliParser.parse(responseData)
    except Exception:
        if session.state.get("auto", False):
            return
        else:
            raise
    return REPLY_FORMAT.format(**parsedData)


@vidInfo.args_parser
@processSession(pluginName=__plugin_name__)
@SyncToAsync
def _(session: CommandSession):
    if session.state.get("id", None):
        return
    args = session.current_arg_text.strip()
    avResult = MATCH_AV.search(args)
    bvResult = MATCH_BV.search(args)
    if avResult:
        session.state["id"] = int(avResult.group(1))
    elif bvResult:
        session.state["id"] = IDCoverter.bv2av(bvResult.group())
    else:
        session.pause("请输入正确的bv号或者av号")


@on_natural_language(only_short_message=False, only_to_me=False)
@SyncToAsync
def _(session: NLPSession):
    status = PluginManager.settings(__plugin_name__, session.ctx).status
    if not status:
        return
    avResult = MATCH_AV.search(session.msg)
    bvResult = MATCH_BV.search(session.msg)
    if avResult:
        return IntentCommand(
            100, name="bilibili_info", args={"id": int(avResult.group(1)), "auto": True}
        )
    elif bvResult:
        return IntentCommand(
            100,
            name="bilibili_info",
            args={"id": IDCoverter.bv2av(bvResult.group()), "auto": True},
        )
    else:
        return


@on_command("bilibili_disable", aliases=("禁用视频信息", "关闭视频信息"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, session.ctx).status = False
    return "视频信息捕捉已关闭"


@on_command("bilibili_enable", aliases=("启用视频信息", "打开视频信息"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, session.ctx).status = True
    return "视频信息捕捉已启用"
