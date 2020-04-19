from copy import deepcopy
from re import compile as compileRegexp

from nonebot import logger, scheduler
from nonebot.command import CommandSession, on_command
from nonebot.permission import GROUP_ADMIN, PRIVATE_FRIEND, SUPERUSER

from utils.decorators import SyncToAsync, WithKeyword
from utils.exception import BotExistError
from utils.manager import PluginManager, nameJoin
from utils.message import processSession

from .config import CONFIG, __plugin_name__
from .network import RefreshFeed, downloadFeed
from .parse import rssParser

PluginManager(__plugin_name__, defaultSettings={"subscribed": {}})
SUBSCRIBE_COMMAND = nameJoin(__plugin_name__, "subscribe")
TEST_COMMAND = nameJoin(__plugin_name__, "test")

URL_MATCH_REGEX = compileRegexp(
    r"(https?|ftp)://((?:\w|\d|[-+&@#/%?=~_|!:,.;])+(?:\w|\d|[-+&@#/%=~_|]))"
)
REFRESH_FEED = RefreshFeed()
POWER_GROUP = GROUP_ADMIN | PRIVATE_FRIEND | SUPERUSER


@on_command(SUBSCRIBE_COMMAND, aliases=("rss订阅", "RSS订阅"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def rssSubscribe(session: CommandSession):
    rssLink: str = session.get("link")
    session.send(f'开始检查订阅源:"{rssLink}"')
    # Get feed data
    rssResource: str = downloadFeed(rssLink)
    rssResourceParse: dict = rssParser(rssResource)
    # Check for duplicates with existing subscriptions
    subscribeToken = rssResourceParse["token"]
    getSettings = PluginManager.settings(__plugin_name__, session.ctx).settings
    if getSettings["subscribed"].get(subscribeToken):
        raise BotExistError(reason="此订阅已存在!")
    else:
        getSettings["subscribed"][subscribeToken] = {
            "link": rssLink,
            "last_update": rssResourceParse["last_update_stamp"],
        }
    # Processing messages
    repeatMessage = "\n".join(
        [
            str(CONFIG.customize.subscribe_repeat).format(**i)
            for i in rssResourceParse["content"][: CONFIG.customize.size]
        ]
    )
    fullMessage = (
        str(CONFIG.customize.subscribe_prefix).format(**rssResourceParse)
        + f"{repeatMessage}\n"
        + str(CONFIG.customize.subscribe_suffix).format(**rssResourceParse)
    )
    PluginManager.settings(__plugin_name__, session.ctx).settings = getSettings
    return fullMessage


@rssSubscribe.args_parser
@processSession
@SyncToAsync
def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    URLSearch = URL_MATCH_REGEX.search(strippedArgs)
    if not URLSearch:
        session.pause("请输入订阅URL")
    session.state["link"] = URLSearch.group()


@scheduler.scheduled_job("interval", minutes=CONFIG.refresh.time)
@SyncToAsync
def scheduledFeedRefresh():
    REFRESH_FEED.run()


@on_command(TEST_COMMAND, aliases=("测试刷新订阅",), permission=SUPERUSER)
@processSession
@SyncToAsync
def _(_: CommandSession):
    REFRESH_FEED.run()
