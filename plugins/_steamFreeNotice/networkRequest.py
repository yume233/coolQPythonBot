from nonebot.log import logger

from asyncRequest import request

from .baseNetwork import multiGet
from .config import *


def _getProxy():
    if PROXY_ADDRESS:
        return {'http': PROXY_ADDRESS, 'https': PROXY_ADDRESS}
    else:
        return {}


async def getGameList() -> dict:
    getParam = {'key': 'STEAMKEY', 'format': 'json'}
    try:
        resp = await request.get(
            url=STEAM_GAMELIST_API, params=getParam, proxies=_getProxy())
        resp = resp.json()
    except request.requestException as e:
        logger.debug('Steam API Game List get Failed!Error:%s' % e)
        resp = {'error': e}
    return resp


async def getGameDetail(gameList: dict) -> list:
    gameAppidList = [app['appid'] for app in gameList['applist']['apps']]
    logger.debug('Get %s Applications' % len(gameAppidList))
    argsList = [(tuple(), {
        'url': STEAM_GAMEDETAIL_API,
        'proxies': _getProxy(),
        'params': {
            'appids': appid
        },
        'timeout': 6
    }) for appid in gameAppidList]
    getThread = multiGet()
    getThread.run(argsList)
    getResult = await getThread.get()
    getThread.stop()
    return getResult
