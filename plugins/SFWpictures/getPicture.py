import aiohttp
import random
import os
import json
from .fakeAsyncRequest import requestsAsync
from requests import RequestException
from uuid import uuid4
from base64 import b64encode

API_ADDRESS = lambda x: 'https://yande.re/post.json?limit=100&page=%d' % x
PROXY_ADDRESS = 'http://127.0.0.1:1081'
MAX_RETRIES = 5
CACHE_DIR = './cache'


async def getImageList() -> dict:
    requestAddress = API_ADDRESS(random.randint(1, 1000))
    # async with aiohttp.ClientSession() as reqSession:
    #     async with reqSession.get(requestAddress, proxy=PROXY_ADDRESS) as resp:
    #         if resp.status == 200:
    #             listData = await resp.json()
    #             listData = {'result': listData}
    #         else:
    #             listData = {'error': resp.status}
    try:
        requestData = await requestsAsync.get(
            requestAddress, proxies=_getProxy())
    except RequestException as e:
        listData = {'error': e}
    else:
        listData = {'result': json.loads(requestData.decode())}
    return listData


async def downloadImage(url) -> dict:
    #timeout = aiohttp.ClientTimeout(10)
    for _ in range(MAX_RETRIES):
        # try:
        #     async with aiohttp.ClientSession() as reqSession, reqSession.get(
        #             url, proxy=PROXY_ADDRESS, timeout=timeout) as resp:
        #         if resp.status == 200:
        #             fileCachePath = _getCacheName('.jpg')
        #             with open(fileCachePath, 'wb') as f:
        #                 while True:
        #                     fileChunk = await resp.content.read(32 * 1024)
        #                     if not fileChunk:
        #                         break
        #                     f.write(fileChunk)
        # except aiohttp.ClientError as e:
        #     print('Async Http Error:', e)
        # else:
        #     break
        try:
            requestResult = await requestsAsync.get(url,proxies=_getProxy(),timeout=(3,None))
        except RequestException as e:
            returnData = {'error':e}
        else:
            returnData = {'result':requestResult}
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