from nonebot import CommandSession, on_command
from nonebot.permission import GROUP_ADMIN, GROUP_MEMBER, SUPERUSER

from asyncRequest import request
from permission import permission

from .config import *
from .infoMatch import getCorrectInfo
from .networkRequest import getSearchResult

__plugin_name__ = 'illustImageSearch'


@on_command(
    'illust_image_search', aliases=('以图搜图', '搜图'), permission=GROUP_MEMBER)
async def illustSearch(session: CommandSession):
    if permission.getDisable(session.ctx, __plugin_name__):
        session.finish('此群搜图功能已被禁用')
    image = session.get('image', prompt='请将图片和搜图指令一同发送')
    await session.send('开始搜索图片')
    status, getResult = await fullBehavior(image)
    if not status:
        session.finish(getResult)
    await session.send(getResult, at_sender=True)


@illustSearch.args_parser
async def _(session: CommandSession):
    for perEndSymbol in END_SYMBOL:
        if perEndSymbol in session.current_arg_text:
            session.finish('指令提前结束,感谢您的使用!')
    if session.current_arg_images:
        imageURL = session.current_arg_images[0]
    else:
        session.pause('请发送一张图片来进行搜索')
    session.state['image'] = imageURL


async def fullBehavior(imageURL: bytes) -> dict:
    searchData = await getSearchResult(imageURL)
    if not searchData:
        return False, '图片搜索失败'
    correctInfo = await getCorrectInfo(searchData)
    resultList = [
        MESSAGE_REPEAT.format(**perSubject)
        for perSubject in correctInfo['subject']
    ]
    fullResult = ''.join(
        resultList[:RETURN_SIZE]) + MESSAGE_SUFFIX.format(**correctInfo)
    return True, fullResult


@on_command('illust_disable', permission=GROUP_ADMIN | SUPERUSER)
async def disable(session: CommandSession):
    permission.disablePlugin(session.ctx, __plugin_name__)
    await session.send('搜图功能已禁用')


@on_command('illust_enable', permission=GROUP_ADMIN | SUPERUSER)
async def enable(session: CommandSession):
    permission.enablePlugin(session.ctx, __plugin_name__)
    await session.send('搜图功能已启用')
