from nonebot import CommandSession, on_command

from utils.decorators import SyncToAsync, WithKeyword
from utils.exception import BotProgramError
from utils.manager import PluginManager
from utils.message import processSession

from .config import Config
from .tools import (determineImageType, imageDownload, processGIF,
                    whatanimeUpload)

__plugin_name__ = 'anime_search'

PluginManager.registerPlugin(__plugin_name__)


@on_command(__plugin_name__, aliases=('以图搜番', '搜番', '以图识番剧'))
@processSession(pluginName=__plugin_name__)
@WithKeyword(keywords=('以图搜番', '以图识番'), command=__plugin_name__)
@SyncToAsync
def animeSearch(session: CommandSession):
    imageLink = session.get('image')
    session.send('开始以图搜番')
    imageRes = imageDownload(imageLink)
    if determineImageType(imageRes) == 'GIF':
        session.send('检测到GIF图片格式,自动截取第一帧上传')
        imageRes = processGIF(imageRes)
    if len(imageRes) >= 1024**2:
        raise BotProgramError('图片大小超过限制,必须小于1MiB,' +
                              f'您的图片大小为{len(imageRes)/1024**2:.3f}MiB')
    searchResult = whatanimeUpload(imageRes)
    messageRepeat = [
        str(Config.customize.repeat).format(**perAnime)
        for perAnime in searchResult['docs']
    ]
    fullMessage = str(Config.customize.prefix).format(**searchResult) +\
        ''.join(messageRepeat[:Config.customize.size]) + \
        str(Config.customize.suffix).format(**searchResult)
    return fullMessage


@animeSearch.args_parser
@processSession
@SyncToAsync
def _(session: CommandSession):
    if session.current_arg_images:
        session.state['image'] = session.current_arg_images[0]
    else:
        session.pause('请发送一张图片来进行搜索')
