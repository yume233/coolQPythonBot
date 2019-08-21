from nonebot import CommandSession, on_command
from base64 import b64encode

from utils.customDecorators import SyncToAsync, WithKeyword
from utils.messageProc import processSession
from utils.pluginManager import manager
from utils.exception import BotProgramError

from .config import Config
from .network import imageDownload, whatanimeUpload

manager.registerPlugin('anime_search')


@on_command('anime_search', aliases=('以图搜番', '搜番', '以图识番剧'))
@processSession(pluginName='anime_search')
@WithKeyword(keywords=('以图搜番', '以图识番'), command='anime_search')
@SyncToAsync
def animeSearch(session: CommandSession):
    imageLink = session.get('image')
    session.send('开始以图搜番')
    imageRes, imageSize = imageDownload(imageLink)
    if imageSize >= 1024**2:
        raise BotProgramError('图片大小超过限制,必须小于1MiB,' +
                              f'您的图片大小为{imageSize/1024**2}MiB')
    searchResult = whatanimeUpload(b64encode(imageRes))
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