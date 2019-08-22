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
        session.state['res'] = texts.replace(' ', '')


@on_command(SEARCH_IMAGE_METHOD, aliases=('p站搜图', '搜索图片'))
@processSession(pluginName=SEARCH_IMAGE_METHOD)
@WithKeyword('p站搜图', command=SEARCH_IMAGE_METHOD)
@SyncToAsync
def searchImage(session: CommandSession):
    keywords = session.get('keyword')
    page = session.get_optional('page', 1)
    session.send(f'开始搜索"{keywords}"的第{page}页')
    apiGet = pixiv.searchIllust(keyword=keywords, page=page)
    apiParse = parseMultiImage(apiGet)
    sortResult = sorted(apiParse['result'],
                        key=lambda x: x['ratio'],
                        reverse=True)
    enableR18 = manager.settings(SEARCH_IMAGE_METHOD,
                                 session.ctx).settings['r-18']
    messageRepeat = [
        str(Config.customize.search_repeat).format(**data)
        for data in sortResult if (not 'R-18' in data['tags']) or enableR18
    ]
    fullMessage = str(Config.customize.search_prefix).format(**apiParse)\
        + ''.join(messageRepeat[:Config.customize.size])\
        + str(Config.customize.search_suffix).format(**apiParse)
    return fullMessage


@searchImage.args_parser
@processSession(pluginName=SEARCH_IMAGE_METHOD)
@SyncToAsync
def _(session: CommandSession):
    if session.current_arg_images:
        session.switch(f'!{GET_IMAGE_METHOD} {session.current_arg}')
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('请输入搜索关键词')
    keywords = strippedArgs.split(' ', 1)
    if len(keywords) == 2:
        page, strippedArgs = keywords
        if page.isdigit():
            session.state['page'] = int(page)
        else:
            strippedArgs = f'{page} {strippedArgs}'
    session.state['keyword'] = strippedArgs


@on_command(MEMBER_IMAGE_METHOD, aliases=('p站画师', '画师', '搜索画师'))
@processSession(pluginName=MEMBER_IMAGE_METHOD)
@WithKeyword('p站画师', '搜索画师')
@SyncToAsync
def memberImage(session: CommandSession):
    memberID = session.get('id')
    page = session.get_optional('page', 1)
    session.send(f'开始获取Pixiv用户ID为{memberID}的作品第{page}页')
    apiGet = pixiv.getMemberIllust(memberID, page)
    apiParse = parseMultiImage(apiGet)
    sortResult = sorted(apiParse['result'],
                        key=lambda x: x['ratio'],
                        reverse=True)
    enableR18 = manager.settings(MEMBER_IMAGE_METHOD,
                                 session.ctx).settings['r-18']
    messageRepeat = [
        str(Config.customize.member_repeat).format(**data)
        for data in sortResult if (not 'R-18' in data['tags']) or enableR18
    ]
    fullMessage = str(Config.customize.member_prefix).format(**apiParse)\
        + ''.join(messageRepeat[:Config.customize.size])\
        + str(Config.customize.member_suffix).format(**apiParse)
    return fullMessage


@memberImage.args_parser
@processSession(pluginName=MEMBER_IMAGE_METHOD)
@SyncToAsync
def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('请输入画师的用户ID')
    if not strippedArgs.replace(' ','').isdigit() \
    or len(strippedArgs.split(' ')) > 2:
        session.pause('您输入的参数不正确')
    splited = strippedArgs.split(' ', 1)
    if len(splited) == 2:
        page, member = splited
        session.state['page'] = int(page)
    else:
        member = strippedArgs
    session.state['id'] = int(member)


@on_command(RANK_IMAGE_METHOD, aliases=('一图', ))
@processSession(pluginName=RANK_IMAGE_METHOD)
@SyncToAsync
def _(session: CommandSession):
    session.send('开始获取一图')
    rank = random.choice(['day', 'week', 'month'])
    apiGet = pixiv.getRank(rank)
    apiParse = parseMultiImage(apiGet)
    choiceResult = random.choice(
        [data for data in apiParse['result'] if data['type'] == 'illust'])
    imageLinks = [i['large']
                  for i in choiceResult['download']][:Config.customize.size]
    images = downloadMutliImage(imageLinks)
    messageRepeat = [str(MessageSegment.image(images[i])) for i in imageLinks]
    fullMessage = str(Config.customize.rank_prefix).format(**choiceResult)\
        + '\n'.join(messageRepeat) + '\n'\
        + str(Config.customize.rank_suffix).format(**choiceResult)
    return fullMessage
