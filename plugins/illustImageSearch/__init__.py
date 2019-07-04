from nonebot import on_command, CommandSession
from .networkRequest import downloadImage, uploadImage
from .infoMatch import getCorrectInfo
from .config import MESSAGE_FORMAT,MESSAGE_SUFFIX,LIST_RANGE,END_SYMBOL


@on_command('illust_image_search', aliases=('以图搜图', '搜图'))
async def illustSearch(session: CommandSession):
    image = session.get('image', prompt='请将图片和搜图指令一同发送')
    if not image:
        session.finish('图片获取失败!')
    getResult = await fullBehavior(image)
    if getResult.get('error'):
        session.finish(getResult['error'])
    await session.send(getResult['result'],at_sender=True)

@illustSearch.args_parser
async def _(session:CommandSession):
    for perEndSymbol in END_SYMBOL:
        if perEndSymbol in session.current_arg_text:
            session.finish('指令提前结束,感谢您的使用!')
    if session.current_arg_images:
        imageURL = session.current_arg_images[0]
        imageRes = await downloadImage(imageURL)
    else:
        session.pause('请发送一张图片来进行搜索')
    session.state['image'] = imageRes

async def fullBehavior(imageRes:bytes) -> dict:
    sauceData = await uploadImage(imageRes)
    print(sauceData)
    if sauceData['header']['status']:
        return {'error':'图片信息上传错误!错误代码:%s'%sauceData['header']['status']}
    cleanData = getCorrectInfo(sauceData)
    resultTextList = []
    for perIllust in cleanData['result']:
        formatedData = MESSAGE_FORMAT.format(**perIllust)
        resultTextList.append(formatedData)
    resultPrefix = ''.join(resultTextList[:LIST_RANGE])
    fullResult = resultPrefix + MESSAGE_SUFFIX.format(**cleanData['header'])
    print(fullResult)
    return {'result':fullResult}