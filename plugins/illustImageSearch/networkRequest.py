import json
from base64 import b64encode
from urllib.parse import urljoin

from nonebot.log import logger
from requests import RequestException

from .config import *
from .fakeAsyncRequest import requestsAsync


async def getSearchResult(imageLink: str) -> bytes:
    getResult = b''
    imageSearchURL = urljoin(ASCII2D_ADDRESS, 'search/url/' + imageLink)
    for _ in range(MAX_RETIRES):
        try:
            getResult = await requestsAsync.get(imageSearchURL)
        except RequestException as e:
            logger.debug('Async Http Request Error:%s' % e)
        else:
            break
    return getResult


async def getPreview(perviewLink: str) -> str:
    try:
        perviewResult = await requestsAsync.get(perviewLink, timeout=6)
        returnData = 'base64://' + b64encode(perviewResult).decode()
    except RequestException as e:
        logger.debug('Async Http Request Error:%s' % e)
        returnData = IMAGE_FALLBACK_ADDRESS
    return returnData


async def createShortLink(links: list):
    urlParams = {'source': str(SHORTLINK_APIKEY), 'url_long': links}
    apiResult = b''
    for _ in range(MAX_RETIRES):
        try:
            apiResult = await requestsAsync.get(
                SHORTLINK_ADDRESS, params=urlParams)
        except RequestException as e:
            logger.debug('Async Http Request Error:%s' % e)
        else:
            break
    if not apiResult:
        raise Exception
    apiLoaded = json.loads(apiResult.decode())
    linkDict = {}
    for perURL in apiLoaded['urls']:
        longURL = perURL['url_long']
        shortURL = perURL['url_short']
        linkDict[longURL] = shortURL
    return linkDict