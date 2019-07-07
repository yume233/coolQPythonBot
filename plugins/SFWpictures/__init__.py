import random
from base64 import b64encode

import aiofiles
from nonebot import (CommandSession, IntentCommand, MessageSegment, on_command,
                     on_natural_language, get_bot)
from nonebot.permission import SUPERUSER, GROUP_ADMIN, check_permission
from nonebot.log import logger

from .config import DISABLE_RANK
from .getPicture import downloadImage, getImageList, changeFileHash


@on_command('setu', aliases=('yande', '色图', '涩图'))
async def getSetu(session: CommandSession):
    rank: str = session.get_optional('rank', 's')
    await session.send('%s级色图装载中……' % rank.upper())
    status, result = await fullBehavior(rank)
    if not status:
        session.finish(result)
    await session.send(result, at_sender=True)


@getSetu.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    userPerm = await check_permission(get_bot(), session.ctx,
                                      GROUP_ADMIN | SUPERUSER)
    if strippedArgs:
        rankList = list('QSE')
        for perRank in list(strippedArgs.upper()):
            if not perRank in rankList:
                await session.finish('评级%s不存在' % perRank)
            if perRank in (list(DISABLE_RANK.upper()) if not userPerm else []):
                await session.finish('%s级色图已被禁用或者是您不配' % perRank)
        session.state['rank'] = strippedArgs


@on_natural_language(keywords=('来一张色图', '我要康色图'))
async def _(session):
    return IntentCommand(80.0, 'setu')


async def fullBehavior(rank: str):
    imgList = await getImageList()
    sendMsg = None
    if imgList.get('error'):
        sendMsg = '涩图列表获取错误,错误:%s' % imgList['error']
    else:
        for _ in range(100):
            choiceResult = random.choice(imgList['result'])
            #print(
            #    _, choiceResult['rating'].upper(), list(rank.upper()), end='')
            if choiceResult['rating'].upper() in list(rank.upper()):
                break
        fileLink = choiceResult['sample_url']
        #print(fileLink)
        fileResult = await downloadImage(fileLink)
        #print(fileCacheDir)
        if fileResult.get('error'):
            sendMsg = '涩图下载错误,原因:%s' % fileResult['error']
    if sendMsg:
        return False, sendMsg
    fileRaw = changeFileHash(fileResult['result'])
    logger.debug('File Top 30 Bytes is %s' % fileRaw[:30])
    messageTemplate = MessageSegment.image('base64://' +
                                           b64encode(fileRaw).decode())
    return True, messageTemplate

@on_command(
    'setu_super', aliases=('超色图', '超涩图'), permission=SUPERUSER | GROUP_ADMIN)
async def getSuperSetu(session: CommandSession):
    session.switch('*setu e')