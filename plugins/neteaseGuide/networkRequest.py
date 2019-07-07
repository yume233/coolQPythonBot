from asyncRequest import request
from nonebot.log import logger
from .config import *


async def _basicJSON(params: dict) -> dict:
    requestAddress = SEARCH_API_ADDRESS if params[
        'type'] == 'search' else API_ADDRESS
    params = {
        'type': params['search_type'],
        's': params['s']
    } if params['type'] == 'search' else params
    try:
        responData = await request.get(requestAddress, params=params)
        responData = responData.json()
        if responData['code'] != 200:
            responData = {'error': responData['code']}
    except request.requestException as e:
        logger.debug('Async Http Request Error:%s' % e)
        responData = {'error': e}
    return responData


class netease:
    @staticmethod
    async def search(keyword: str):
        argsPayload = {'type': 'search', 'search_type': 1, 's': keyword}
        getData = await _basicJSON(argsPayload)
        return getData

    @staticmethod
    async def searchAlbum(keyword: str):
        argsPayload = {'type': 'search', 'search_type': 10, 's': keyword}
        getData = await _basicJSON(argsPayload)
        return getData

    @staticmethod
    async def searchArtist(keyword: str):
        argsPayload = {'type': 'search', 'search_type': 100, 's': keyword}
        getData = await _basicJSON(argsPayload)
        return getData

    @staticmethod
    async def searchMix(keyword: str):
        argsPayload = {'type': 'search', 'search_type': 1000, 's': keyword}
        getData = await _basicJSON(argsPayload)
        return getData

    @staticmethod
    async def getSongDetail(songID: int):
        argsPayload = {'type': 'detail', 'id': songID}
        getData = await _basicJSON(argsPayload)
        return getData

    @staticmethod
    async def getAlbumDetail(albumID: int):
        argsPayload = {'type': 'album', 'id': albumID}
        getData = await _basicJSON(argsPayload)
        return getData

    @staticmethod
    async def getArtistDetail(artistID: int):
        argsPayload = {'type': 'artist', 'id': artistID}
        getData = await _basicJSON(argsPayload)
        return getData

    @staticmethod
    async def getMixDetail(mixID: int):
        argsPayload = {'type': 'playlist', 'id': mixID}
        getData = await _basicJSON(argsPayload)
        return getData