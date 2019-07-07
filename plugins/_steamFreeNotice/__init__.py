import nonebot
import json
from nonebot.log import logger
from nonebot import on_command,CommandSession
from nonebot.permission import SUPERUSER

from .databaseOperating import database
from .networkRequest import getGameList, getGameDetail


@nonebot.scheduler.scheduled_job('cron', hour='*')
async def _():
    botObject = nonebot.get_bot()
    steamGameList = await getGameList()
    if steamGameList.get('error') != None:
        logger.debug('Steam Free Checker Error:%s'%steamGameList['error'])
    steamDetailList = await getGameDetail(steamGameList)
    dbDetail = []
    for perDetail in steamDetailList:
        if perDetail.get('error') != None:
            logger('Steam Free Check Error:%s'%perDetail['error'])
            continue
        for detailID in perDetail:
            gameDetail = perDetail[detailID]
            if not gameDetail['success']:
                continue
            gameDetail = gameDetail['data']
            dbDetail.append((
                gameDetail['steam_appid'],
                gameDetail['name'],
                gameDetail['type'],
                gameDetail['short_description'],
                json.dumps(gameDetail)
            ))
    db = database()
    db.addMulti(dbDetail)

@on_command('steam_free',permission=SUPERUSER)
async def _(session:CommandSession):
    steamGameList = await getGameList()
    if steamGameList.get('error') != None:
        logger.debug('Steam Free Checker Error:%s'%steamGameList['error'])
    steamDetailList = await getGameDetail(steamGameList)

def someBehavior(gameList:list):
    dbDetail = []
    for perDetail in gameList:
        if perDetail.get('error') != None:
            logger.debug('Steam Free Check Error:%s'%perDetail['error'])
            continue
        for detailID in perDetail:
            gameDetail = perDetail[detailID]
            if not gameDetail['success']:
                continue
            gameDetail = gameDetail['data']
            dbDetail.append((
                gameDetail['steam_appid'],
                gameDetail['name'],
                gameDetail['type'],
                gameDetail['short_description'],
                json.dumps(gameDetail)
            ))
    db = database()
    db.addMulti(dbDetail)