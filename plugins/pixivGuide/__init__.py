import re
from nonebot import CommandSession, on_command, MessageSegment, on_natural_language, IntentCommand

from .config import RESULT_SIZE, ALLOW_R18
from .networkRequest import pixiv


@on_command('pixiv_getimage', aliases=('点图', '获取图片'))
async def pixivGetImage(session: CommandSession):
    imageID = session.get('id', prompt='pixiv的图片ID')
    imageResloution = session.get_optional('res', '大图')
    await session.send('开始获取图片%s的%s' % (imageID, imageResloution))
    apiDetail = await pixiv.getImageDetail(int(imageID))
    if apiDetail.get('error'):
        session.finish('图片获取失败,原因:%s' % apiDetail['error'])
    if not ALLOW_R18:
        for perTag in apiDetail['illust']['tags']:
            if perTag['name'] == 'R-18':
                session.finish('图片获取失败,原因:NSFW')
    imageLink = []
    if apiDetail['illust']['page_count'] == 1:
        addData = {'image_urls': {}}
        addData['image_urls'].update(apiDetail['illust']['image_urls'])
        addData['image_urls']['original'] = apiDetail['illust'][
            'meta_single_page']['original_image_url']
        print(addData)
        apiDetail['illust']['meta_pages'].append(addData)
    for perPicture in apiDetail['illust']['meta_pages'][:RESULT_SIZE]:
        perPicture = perPicture['image_urls']
        if imageResloution == '大图':
            imageLink.append(perPicture['large'])
        elif imageResloution == '小图':
            imageLink.append(perPicture['medium'])
        elif imageResloution == '原图':
            imageLink.append(perPicture['original'])
    imageResult = []
    for perLink in imageLink:
        imgLink = await pixiv.downloadImage(perLink)
        imageSeg = str(MessageSegment.image(imgLink))
        print(imageSeg)
        imageResult.append(imageSeg)
    await session.send('\n'.join(imageResult), at_sender=True)


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

@on_command('pixiv_searchimage',aliases=('搜图','搜索图片'))
async def pixivSearchImage(session:CommandSession):
    keyword = session.get('keyword',prompt='搜索关键词')
    apiResult = await pixiv.searchIllust(keyword)
    if apiResult.get('error') != None:
        session.finish('图片搜索出错,原因:%s'%apiResult['error'])
    