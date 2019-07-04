from .config import *
from .animeSearchAPI import searchAnimeByScreenshot
from .imageCache import downloadImage
from nonebot import CommandSession, on_command


@on_command('anime_screenshot_search', aliases=('以图搜番', '搜番'))
async def animeSearch(session: CommandSession):
    imageResource = session.get('image', prompt='请将图片和搜番指令一同发送')
    result = await searchAnimeByScreenshot(imageResource)
    if result.get('error'):
        await session.send('图片搜索失败,错误码%d' % result['error'])
    else:
        resultList = []
        for perDoc in result['docs']:
            result = '''
            ------------------------
            番剧名称:{anime}
            英文名:{title_english}
            起止时间:{from}s-{to}s
            相似度:{similarity:.4%}
            '''.format(**perDoc)
            resultList.append(result)
        if resultList:
            returnResult = ''.join(resultList)
        else:
            returnResult = '没有找到相关番剧'
        await session.send(returnResult)


@animeSearch.args_parser
async def _(session: CommandSession):
    if session.current_arg_images:
        imgUrl = session.current_arg_images[0]
        imgLocalPath, imgSize = await downloadImage(imgUrl)
    else:
        session.pause('没得图片你叫我玩啥?')
    if imgSize >= 1024**2:
        session.pause('图片大小超过限制!必须小于1MB,您的图片为%.3fMB' % imgSize / 1024**2)
    session.state['image'] = imgLocalPath
    return
