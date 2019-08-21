import random

from nonebot import CommandSession, MessageSegment, on_command
from nonebot.permission import GROUP_ADMIN, PRIVATE_FRIEND, SUPERUSER

from utils.customDecorators import SyncToAsync, WithKeyword
from utils.exception import BotDisabledError
from utils.messageProc import processSession
from utils.pluginManager import manager, nameJoin

from .config import Config
from .network import downloadImage, downloadMutliImage, pixiv
from .parse import parseMultiImage, parseSingleImage

GET_IMAGE_METHOD = nameJoin('pixiv', 'get')
SEARCH_IMAGE_METHOD = nameJoin('pixiv', 'search')
MEMBER_IMAGE_METHOD = nameJoin('pixiv', 'member')
RANK_IMAGE_METHOD = nameJoin('pixiv', 'rank')
POWER_GROUP = (GROUP_ADMIN | SUPERUSER | PRIVATE_FRIEND)

manager.registerPlugin(GET_IMAGE_METHOD, defaultSettings={'r-18': False})
manager.registerPlugin(SEARCH_IMAGE_METHOD, defaultSettings={'r-18': False})
manager.registerPlugin(MEMBER_IMAGE_METHOD, defaultSettings={'r-18': False})
manager.registerPlugin(RANK_IMAGE_METHOD)


@on_command(GET_IMAGE_METHOD, aliases=('点图', '获取图片'))
@processSession(pluginName=GET_IMAGE_METHOD)
@WithKeyword('p站点图', command=GET_IMAGE_METHOD)
@SyncToAsync
def getImage(session: CommandSession):
    imageID = session.get('id')
    imageResloution = session.get_optional('res', '大图')
    session.send(f'开始获取Pixiv ID为{imageID}的{imageResloution}')
    apiGet = pixiv.getImageDetail(imageID)
    apiParse = parseSingleImage(apiGet)
    allowR18 = manager.settings(GET_IMAGE_METHOD,
                                ctx=session.ctx).settings['r-18']
    if ('R-18' in apiParse['tags']) and not allowR18:
        raise BotDisabledError('不允许NSFW图片')
    imageURLs = [{
        '大图': p['large'],
        '小图': p['medium'],
        '原图': p['original']
    }[imageResloution] for p in apiParse['download']][:Config.customize.size]
    imageDownloaded = downloadMutliImage(imageURLs)
    images = [str(MessageSegment.image(imageDownloaded[i])) for i in imageURLs]
    repeatMessage = '\n'.join(images)
    finalMessage = str(Config.customize.image_prefix).format(**apiParse)\
        + f'{repeatMessage}\n'\
        + str(Config.customize.image_suffix).format(**apiParse)
    return finalMessage


@getImage.args_parser
@processSession(pluginName=GET_IMAGE_METHOD)
@SyncToAsync
def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    digits = ''.join([i for i in list(strippedArgs) if i.isdigit()])
    texts = ''.join(i for i in list(strippedArgs) if i not in list(digits))
    if not (strippedArgs and digits):
        session.pause('请输入p站图片ID')
    session.state['id'] = int(digits)
    if texts:
        session.state['res'] = texts