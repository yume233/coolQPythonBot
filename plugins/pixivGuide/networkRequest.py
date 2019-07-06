import json
from asyncio import sleep
from base64 import b64encode
from queue import Queue
from threading import Thread

from nonebot.log import logger
from PIL import Image
from requests import RequestException

from .config import *
from .fakeAsyncRequest import requestsAsync
from .tmpFile import tmpFile


def _convertImage(imageRes: bytes) -> bytes:
    with tmpFile() as readFilename:
        with tmpFile() as writeFilename:
            with open(readFilename, 'wb') as f:
                f.write(imageRes)
            with Image.open(readFilename) as img:
                img.save(writeFilename, 'PNG')
            with open(readFilename, 'rb') as f:
                readRes = f.read()
    return readRes


def _getProxies():
    if IMAGE_PROXY:
        return {'http': IMAGE_PROXY, 'https': IMAGE_PROXY}
    else:
        return {}


async def _basicGetJSON(params: dict) -> dict:
    try:
        responData = await requestsAsync.get(API_ADDRESS, params=params)
        responData = json.loads(responData.decode())
        if responData.get('error'):
            responData['error'] = responData['error']['message'] + responData[
                'error']['user_message'] + responData['error']['reason']
    except RequestException as e:
        logger.debug('Async Http Error:%s' % e)
        responData = {'error': e}
    return responData


class pixiv:
    @staticmethod
    async def downloadImage(url) -> str:
        headers = {'Referer': 'https://www.pixiv.net'}
        for _ in range(MAX_RETRIES):
            try:
                responData = await requestsAsync.get(
                    url,
                    headers=headers,
                    timeout=(3, None),
                    proxies=_getProxies())
            except RequestException as e:
                logger.debug('Async Http Error:%s' % e)
                responData = b''
            else:
                break
        if responData:
            convertedData = _convertImage(responData)
            print(convertedData[:50])
            return 'base64://' + b64encode(convertedData).decode()
        else:
            return IMAGE_FALLBACK

    @staticmethod
    async def getRank(rankLevel: str = 'week') -> dict:
        argsPayload = {'type': 'rank', 'mode': rankLevel}
        getData = await _basicGetJSON(argsPayload)
        return getData

    @staticmethod
    async def searchIllust(keyword: str,
                           searchMode: int = 0,
                           ascending: bool = False) -> dict:
        searchModeString = (
            'partial_match_for_tags' if searchMode == 0 else
            'exact_match_for_tags' if searchMode == 1 else 'title_and_caption')
        argsPayload = {
            'type': 'search',
            'word': keyword,
            'mode': searchModeString,
            'order': 'date_asc' if ascending else 'date_desc'
        }
        getData = await _basicGetJSON(argsPayload)
        return getData

    @staticmethod
    async def getRelatedIllust(imageID: int) -> dict:
        argsPayload = {'type': 'related', 'id': str(imageID)}
        getData = await _basicGetJSON(argsPayload)
        return getData

    @staticmethod
    async def getHotTags():
        argsPayload = {'type': 'tags'}
        getData = await _basicGetJSON(argsPayload)
        return getData

    @staticmethod
    async def getImageDetail(imageID: int) -> dict:
        argsPayload = {'type': 'illust', 'id': str(imageID)}
        getData = await _basicGetJSON(argsPayload)
        return getData

    @staticmethod
    async def getMemberDetail(memberID: int) -> dict:
        argsPayload = {'type': 'member', 'id': str(memberID)}
        getData = await _basicGetJSON(argsPayload)
        return getData

    @staticmethod
    async def getMemberIllust(memberID: int) -> dict:
        argsPayload = {'type': 'member_illust', 'id': str(memberID)}
        getData = await _basicGetJSON(argsPayload)
        return getData
