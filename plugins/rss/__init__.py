from binascii import crc32
from re import compile as compileRegexp

from nonebot import logger
from nonebot.command import CommandSession, on_command

from utils.decorators import SyncToAsync, WithKeyword
from utils.manager import PluginManager, nameJoin
from utils.message import processSession
from utils.exception import BotExistError

from .config import CONFIG
from .network import downloadFeed
from .parse import rssParser

__plugin_name__ = 'rss'
PluginManager(__plugin_name__, defaultSettings={'subscribed': {}})
SUBSCRIBE_COMMAND = nameJoin(__plugin_name__, 'subscribe')
URL_MATCH_REGEX = compileRegexp(
    r'(https?|ftp)://((?:\w|\d|[-+&@#/%?=~_|!:,.;])+(?:\w|\d|[-+&@#/%=~_|]))')


@on_command(SUBSCRIBE_COMMAND, aliases=('rss订阅', 'RSS订阅'))
@processSession
@SyncToAsync
def rssSubscribe(session: CommandSession):
    rssLink: str = session.get('link')
    session.send(f'开始检查订阅源:"{rssLink}"')
    subscribeToken = f'{crc32(rssLink.encode()):x}'.upper()
    pluginSettings = PluginManager.settings(__plugin_name__, session.ctx)
    getSettings = pluginSettings.settings
    if getSettings['subscribed'].get(subscribeToken):
        raise BotExistError(reason='此订阅已存在!')
    else:
        getSettings['subscribed'][subscribeToken] = rssLink
    rssResource: str = downloadFeed(rssLink)
    rssResourceParse: dict = rssParser(rssResource)
    rssResourceParse.update({'token': subscribeToken})
    repeatMessage = '\n'.join([
        str(CONFIG.customize.subscribe_repeat).format(**i)
        for i in rssResourceParse['content'][:CONFIG.customize.size]
    ])
    fullMessage = str(CONFIG.customize.subscribe_prefix).format(**rssResourceParse) \
        + f'{repeatMessage}\n' \
        + str(CONFIG.customize.subscribe_suffix).format(**rssResourceParse)
    pluginSettings.settings = getSettings
    return fullMessage


@rssSubscribe.args_parser
@processSession
@SyncToAsync
def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    URLSearch = URL_MATCH_REGEX.search(strippedArgs)
    if not URLSearch:
        session.pause('请输入订阅URL')
    session.state['link'] = URLSearch.group()