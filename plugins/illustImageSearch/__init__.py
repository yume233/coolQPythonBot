from nonebot import on_command, CommandSession
from .infoMatch import getCorrectInfo
from .fakeAsyncRequest import requestsAsync
from .config import *


@on_command('illust_image_search', aliases=('以图搜图', '搜图'))
async def illustSearch(session: CommandSession):
    image = session.get('image', prompt='请将图片和搜图指令一同发送')
    status,getResult = await fullBehavior(image)
    if not status:
        session.finish(getResult)
    await session.send(getResult,at_sender=True)

@illustSearch.args_parser
async def _(session:CommandSession):
    for perEndSymbol in END_SYMBOL:
        if perEndSymbol in session.current_arg_text:
            session.finish('指令提前结束,感谢您的使用!')
    if session.current_arg_images:
        imageURL = session.current_arg_images[0]
    else:
        session.pause('请发送一张图片来进行搜索')
    session.state['image'] = imageURL

async def fullBehavior(imageURL:bytes) -> dict:
    imageSearchURL = ASCII2D_ADDRESS + 'search/url/' + imageURL
    searchData = await requestsAsync.get(imageSearchURL)
    if not searchData:
        return False,'图片搜索失败'
    correctInfo = await getCorrectInfo(searchData.decode())
    resultList = []
    for perSubject in correctInfo['subject']:
        singleMessage = MESSAGE_REPEAT.format(**perSubject)
        resultList.append(singleMessage)
    fullResult = ''.join(resultList) + MESSAGE_SUFFIX
    return True,fullResult