import os

import requests
from nonebot import CommandSession, on_command

from utils.configsReader import configsReader, copyFileInText
from utils.decorators import Async, WithKeyword
from utils.exception import BotRequestError
from utils.message import processSession
from utils.manager import PluginManager

__plugin_name__ = 'hitokoto'

CONFIG_PATH = 'configs/hitokoto.yml'
DEFAULT_PATH = 'configs/default.hitokoto.yml'

if not os.path.isfile(CONFIG_PATH):
    copyFileInText(DEFAULT_PATH, CONFIG_PATH)

CONFIG_READ = configsReader(CONFIG_PATH, DEFAULT_PATH)

PluginManager.registerPlugin(__plugin_name__)


@on_command(__plugin_name__, aliases=('一言', ))
@processSession(pluginName=__plugin_name__)
@WithKeyword(('一言哥', '来句一言'), __plugin_name__)
@Async
def hitokoto(session: CommandSession):
    try:
        result = requests.get(CONFIG_READ.api_address)
        result.raise_for_status()
        result = result.json()
    except requests.RequestException:
        raise BotRequestError
    return str(CONFIG_READ.reply_format).format(**result), False
