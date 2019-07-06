import re

from nonebot import (
    CommandSession, IntentCommand, MessageSegment, on_command,
    on_natural_language)
from nonebot.log import logger

from .config import *
from .infoParse import parseMultiImage, parseSingleImage
from .networkRequest import pixiv


@on_command('pixiv_getimage', aliases=('点图', '获取图片'))
async def pixivGetImage(session: CommandSession):
    imageID = session.get('id', prompt='pixiv的图片ID')
    imageResloution = session.get_optional('res', '大图')
    await session.send('开始获取图片%s的%s' % (imageID, imageResloution))
    apiDetail = await pixiv.getImageDetail(int(imageID))
    if apiDetail.get('error') != None:
        session.finish('图片获取失败,原因:%s' % apiDetail['error'])
    imageData = parseSingleImage(apiDetail)
    if not ALLOW_R18:
        if 'R-18' in imageData['tags']:
            session.finish('图片获取失败,原因:NSFW')
    imageLinks = []
    for perPicture in imageData['download']:
        imageLinks.append({
            '大图': perPicture['large'],
            '小图': perPicture['medium'],
            '原图': perPicture['original']
        }[imageResloution])
    imageResult = []
    for perLink in imageLinks:
        logger.debug('Will Download %s' % perLink)
        imageLocalLink = await pixiv.downloadImage(perLink)
        imageSegment = str(MessageSegment.image(imageLocalLink))
        logger.debug('Image Link Top 30 Letters:%s' % imageLocalLink[:30])
        imageResult.append(imageSegment)
    sendMessage = GETIMAGE_PREFIX.format(
        **imageData) + '\n'.join(imageResult) + GET_IMAGE_SUFFIX.format(
            **imageData)
    await session.send(sendMessage, at_sender=True)


@pixivGetImage.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if re.search(r'\d+', strippedArgs):
        session.state['id'] = re.search(r'\d+', strippedArgs).group()
    else:
        session.pause('请输入p站图片ID')
    for perKeyword in ('大图', '小图', '原图'):
        if perKeyword in strippedArgs:
            session.state['res'] = perKeyword


@on_natural_language(keywords=('p站点图'), only_short_message=True)
async def _(session):
    return IntentCommand(70.0, 'pixiv_getimage')


@on_command('pixiv_searchimage', aliases=('p站搜图', '搜索图片'))
async def pixivSearchImage(session: CommandSession):
    keyword = session.get('keyword', prompt='搜索关键词缺失')
    pageNumber = session.get_optional('pn', default=1)
    sortSet = session.get_optional('sort', default=False)
    await session.send('开始搜索“%s”的第%d页' % (keyword, pageNumber))
    apiResult = await pixiv.searchIllust(
        keyword, page=pageNumber, ascending=sortSet)
    if apiResult.get('error') != None:
        session.finish('图片搜索出错,原因:%s' % apiResult['error'])
    parseResult = parseMultiImage(apiResult)
    sortResult = sorted(parseResult['result'], key=lambda x: x['ratio'],reverse=True)
    repeatMessage = [
        SEARCH_IMAGE_REPEAT.format(**data) for data in sortResult
        if (not 'R-18' in data['tags']) or ALLOW_R18
    ]
    fullMessage = SEARCH_IMAGE_PREFIX.format(**parseResult) + ''.join(
        repeatMessage[:RESULT_SIZE]) + SEARCH_IMAGE_SUFFIX.format(
            **parseResult)
    await session.send(fullMessage, at_sender=True)


@pixivSearchImage.args_parser
async def _(session: CommandSession):
    if session.current_arg_images:
        session.switch('*illust_image_search ' + session.current_arg)
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('请输入搜索关键词')
    outArgs = strippedArgs.split(' ')
    if len(outArgs) > 1:
        if outArgs[0].isdigit():
            session.state['pn'] = int(outArgs[0])
            keyword = ' '.join(outArgs[1:])
        else:
            keyword = strippedArgs
    session.state['keyword'] = keyword


@on_natural_language(keywords=('p站搜图'))
async def _(session):
    return IntentCommand(70, 'pixiv_searchimage')
