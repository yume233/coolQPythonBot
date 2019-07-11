import random
from base64 import b64encode

from nonebot import (CommandSession, IntentCommand, MessageSegment, get_bot,
                     on_command, on_natural_language)
from nonebot.log import logger
from nonebot.permission import GROUP_ADMIN, SUPERUSER, check_permission

from permission import permission

from .config import DISABLE_RANK, MAX_SEND
from .getPicture import changeFileHash, downloadImage, getImageList
from .permissionManager import *

__plugin_name__ = 'SFWPictures'


@on_command('setu', aliases=('yande', '色图', '涩图'))
async def getSetu(session: CommandSession):
    rank: str = session.get_optional('rank', 's')
    picNum: int = session.get_optional('num', 1)
    picNum = picNum if picNum <= MAX_SEND else 3
    await session.send('%s级色图装载中……将连续发送%s张图片' % (rank.upper(), picNum))
    for _ in range(picNum):
        status, result = await fullBehavior(rank)
        if not status:
            session.finish(result)
        await session.send(result, at_sender=True)


@getSetu.args_parser
async def _setuArgsParser(session: CommandSession):
    isDisable = permission.getDisable(session.ctx, __plugin_name__)
    if isDisable:
        session.finish('涩图功能已经被禁用!')
    notAvalRank = permission.getSettings(
        session.ctx, __plugin_name__,
        {'aval': list(DISABLE_RANK.upper())})['aval']
    strippedArgs = session.current_arg_text.strip()
    userPerm = await check_permission(get_bot(), session.ctx,
                                      GROUP_ADMIN | SUPERUSER)
    if not strippedArgs:
        return
    if len(strippedArgs.split(' ', 1)) == 2:
        strippedArgs, picNum = strippedArgs.split(' ', 1)
        if not picNum.isdigit:
            strippedArgs = strippedArgs + picNum
        else:
            session.state['num'] = int(picNum)
    rankList = list('QSE')
    for perRank in list(strippedArgs.upper()):
        if not perRank in rankList:
            await session.finish('评级%s不存在' % perRank)
        if perRank in (notAvalRank if not userPerm else []):
            await session.finish('%s级色图已被禁用' % perRank)
    session.state['rank'] = strippedArgs


@on_natural_language(keywords=('来一张色图', '我要康色图'))
async def _setuNLP(session):
    return IntentCommand(70.0, 'setu')


async def fullBehavior(rank: str):
    imgList = await getImageList()
    sendMsg = None
    if imgList.get('error'):
        sendMsg = '涩图列表获取错误,错误:%s' % imgList['error']
    else:
        if not imgList['result']:
            return True, '(假装自己是涩图)'
        for _ in range(100):
            choiceResult = random.choice(imgList['result'])
            if choiceResult['rating'].upper() in list(rank.upper()):
                break
        fileLink = choiceResult['sample_url']
        fileResult = await downloadImage(fileLink)
        if fileResult.get('error'):
            sendMsg = '涩图下载错误,原因:%s' % fileResult['error']
    if sendMsg:
        return False, sendMsg
    fileRaw = changeFileHash(fileResult['result'])
    encodedImage = b64encode(fileRaw).decode()
    logger.debug('Top 30 Setu Encoded is %s' % encodedImage[:30])
    messageTemplate = MessageSegment.image('base64://' +
                                           b64encode(fileRaw).decode())
    return True, messageTemplate
