from nonebot import CommandSession, on_command
from nonebot.permission import GROUP_ADMIN, PRIVATE_FRIEND, SUPERUSER

from utils.decorators import SyncToAsync, WithKeyword
from utils.manager import PluginManager
from utils.message import processSession

from .config import Config
from .parse import getCorrectInfo, searchImage

__plugin_name__ = "illust_search"

PluginManager.registerPlugin(__plugin_name__, defaultStatus=False)
POWER_GROUP = GROUP_ADMIN | SUPERUSER | PRIVATE_FRIEND


@on_command(__plugin_name__, aliases=("以图搜图", "搜图"))
@processSession(pluginName=__plugin_name__)
@WithKeyword("以图搜图", command=__plugin_name__)
@SyncToAsync
def illustSearch(session: CommandSession):
    imageURL = session.get("image")
    session.send("开始以图搜图")
    searchContent = searchImage(imageURL)
    searchParse = getCorrectInfo(searchContent)
    messageRepeat = [
        str(Config.customize.repeat).format(**subject)
        for subject in searchParse["subject"]
    ]
    fullMessage = (
        str(Config.customize.prefix).format(**searchParse)
        + "".join(messageRepeat[: Config.customize.size])
        + str(Config.customize.suffix).format(**searchParse)
    )
    return fullMessage


@illustSearch.args_parser
@processSession(pluginName=__plugin_name__)
@SyncToAsync
def _(session: CommandSession):
    if session.current_arg_images:
        session.state["image"] = session.current_arg_images[0]
    else:
        session.pause("请发送一张图片来进行搜索")


@on_command("illust_search_enable", aliases=("启用搜图", "打开以图搜图"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, ctx=session.ctx).status = True
    return "搜图功能已启用", False


@on_command("illust_search_disable", aliases=("禁用搜图", "关闭以图搜图"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, ctx=session.ctx).status = False
    return "搜图功能已禁用", False
