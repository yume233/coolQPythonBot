from nonebot.log import logger

from asyncRequest import request

from .config import *


async def _baseJson(params: dict) -> dict:
    getAddress = {
        'timeline': TIMELINE_ADDRESS,
        'season': ANIME_INFO_ADDRESS
    }.get(params['get'], API_ADDRESS)
    try:
        resp = await request.get(getAddress, params=params)
        resp = resp.json()
        if resp['code']:
            resp = {'error': resp['message']}
    except request.requestException as e:
        resp = {'error': e}
    return resp


class bilibili:
    @staticmethod
    async def getSpace(uid: int):
        argsParam = {'get': 'space', 'vmid': uid}
        respData = await _baseJson(argsParam)
        return respData

    @staticmethod
    async def getAnimeTimeline():
        argsParam = {'get': 'timeline'}
        respData = await _baseJson(argsParam)
        return respData

    @staticmethod
    async def getAnimeInfo(seasonID: int):
        argsParam = {'get': 'season', 'season': seasonID}
        respData = await _baseJson(argsParam)
        return respData

    @staticmethod
    async def search(keyword: str):
        argsParam = {'get': 'search', 'keyword': keyword}
        respData = await _baseJson(argsParam)
        return respData
