import json
from base64 import b64encode
from urllib.parse import urljoin

from nonebot.log import logger
from requests import RequestException

from asyncRequest import request

from .config import *


async def getSearchResult(imageLink: str) -> str:
    getResult = ''
    imageSearchURL = urljoin(ASCII2D_ADDRESS, 'search/url/' + imageLink)
    for _ in range(MAX_RETIRES):
        try:
            getResult = await request.get(
                imageSearchURL, timeout=6, proxies=_getProxies())
            getResult = getResult.text()
        except RequestException as e:
            logger.debug('Async Http Request Error:%s' % e)
        else:
            break
    return getResult


async def getPreview(perviewLink: str) -> str:
    try:
        perviewResult = await request.get(perviewLink, timeout=6)
        returnData = 'base64://' + b64encode(perviewResult.content).decode()
    except RequestException as e:
        logger.debug('Async Http Request Error:%s' % e)
        returnData = IMAGE_FALLBACK_ADDRESS
    return returnData


async def createShortLink(links: list):
    urlParams = {'source': str(SHORTLINK_APIKEY), 'url_long': links}
    apiResult = None
    if not links:
        return {}
    for _ in range(MAX_RETIRES):
        try:
            apiResult = await request.get(SHORTLINK_ADDRESS, params=urlParams)
        except RequestException as e:
            logger.debug('Async Http Request Error:%s' % e)
        else:
            break
    if not apiResult:
        raise Exception
    apiLoaded = apiResult.json()
    linkDict = {
        perURL['url_long']: perURL['url_short']
        for perURL in apiLoaded['urls']
    }
    return linkDict


def _getProxies():
    if PROXY_ADDRESS:
        return {'http': PROXY_ADDRESS, 'https': PROXY_ADDRESS}
    else:
        return {}
