import json
import os
import random
from base64 import b64encode
from uuid import uuid4
from secrets import token_bytes

import aiohttp
from requests import RequestException

from .config import *
from asyncRequest import request


def changeFileHash(originFile: bytes) -> bytes:
    fileAdd = b'\x00' * 16 + token_bytes(16)
    return originFile + fileAdd


async def getImageList() -> dict:
    getAddr = API_ADDRESS if random.random() >= .5 else API_ADDRESS_2
    requestAddress = getAddr(random.randint(1, 1000))
    try:
        requestData = await request.get(requestAddress, proxies=_getProxy())
    except RequestException as e:
        listData = {'error': e}
    else:
        listData = {'result': requestData.json()}
    return listData


async def downloadImage(url) -> dict:
    for _ in range(MAX_RETRIES):
        try:
            requestResult = await request.get(url,
                                              proxies=_getProxy(),
                                              timeout=(1.5, None))
        except RequestException as e:
            returnData = {'error': e}
        else:
            returnData = {'result': requestResult.content}
            break
    return returnData


def _getCacheName(ext: str = ''):
    cacheFilePath = os.path.join(CACHE_DIR, uuid4().hex.upper() + ext)
    fullCacheFilePath = os.path.abspath(cacheFilePath)
    return fullCacheFilePath


def _getProxy():
    if PROXY_ADDRESS:
        return {'http': PROXY_ADDRESS, 'https': PROXY_ADDRESS}
    else:
        return {}
