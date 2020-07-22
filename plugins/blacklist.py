from aiocqhttp import Event
from nonebot import CommandSession, NoneBot, on_command, MessageSegment
from nonebot.command.argfilter.extractors import extract_numbers
from nonebot.message import CanceledException, message_preprocessor
from nonebot.permission import GROUP_ADMIN, SUPERUSER

from utils.botConfig import settings
from utils.decorators import SyncToAsync
from utils.objects import callModuleAPI
from utils.manager import PluginManager
from utils.message import processSession

__plugin_name__ = "blacklist"
POWER_GROUP = GROUP_ADMIN | SUPERUSER

PluginManager.registerPlugin(__plugin_name__, defaultSettings=[])


@message_preprocessor
async def _(bot: NoneBot, event: Event, _):
    if event.user_id in settings.SUPERUSERS:
        return
    if "group_id" not in event:
        return
    blacklists = PluginManager.settings(__plugin_name__, event).settings
    if event.user_id in blacklists:
        raise CanceledException(f"User {event.user_id} is in blacklist")


@on_command("blacklist_add", aliases=("黑名单添加", "拉黑"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    banID = extract_numbers(session.current_arg_text)
    groupUsers = [
        i["user_id"]
        for i in callModuleAPI(
            "get_group_member_list", params={"group_id": session.event.group_id}
        )
    ]
    banID = [*set([int(i) for i in banID]).intersection({*groupUsers})]
    if not banID:
        session.pause("请输入被拉黑者的QQ")
    nowBlacklist: list = PluginManager.settings(__plugin_name__, session.event).settings
    nowBlacklist.extend(map(int, banID))
    PluginManager.settings(__plugin_name__, session.event).settings = [
        *set(nowBlacklist)
    ]
    return "已经为" + "".join(map(lambda x: str(MessageSegment.at(x)), banID)) + "添加黑名单"


@on_command("blacklist_remove", aliases=("黑名单移除", "洗白"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    banID = extract_numbers(session.current_arg_text)
    if not banID:
        session.pause("请输入被洗白者的QQ")
    nowBlacklist: list = PluginManager.settings(__plugin_name__, session.event).settings
    nowBlacklist = [i for i in nowBlacklist if i not in banID]
    PluginManager.settings(__plugin_name__, session.event).settings = [
        *set(nowBlacklist)
    ]
    return "已经为" + "".join(map(lambda x: str(MessageSegment.at(x)), banID)) + "移除黑名单"


@on_command("blacklist_view", aliases=("查看黑名单", "黑人"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    nowBlacklist: list = PluginManager.settings(__plugin_name__, session.event).settings
    return (
        "目前" + "".join(map(lambda x: str(MessageSegment.at(x)), nowBlacklist)) + "在黑名单上"
    )
