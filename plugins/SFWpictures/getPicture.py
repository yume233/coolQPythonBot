import json
import os
import random
from base64 import b64encode
from uuid import uuid4

import aiohttp
from requests import RequestException

from .config import *
from .fakeAsyncRequest import requestsAsync


async def getImageList() -> dict:
    requestAddress = API_ADDRESS(random.randint(1, 1000))
    try:
        requestData = await requestsAsync.get(
            requestAddress, proxies=_getProxy())
    except RequestException as e:
        listData = {'error': e}
    else:
        listData = {'result': json.loads(requestData.decode())}
    return listData


async def downloadImage(url) -> dict:
    for _ in range(MAX_RETRIES):
        try:
            requestResult = await requestsAsync.get(
                url, proxies=_getProxy(), timeout=(3, None))
        except RequestException as e:
            returnData = {'error': e}
        else:
            returnData = {'result': requestResult}
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
