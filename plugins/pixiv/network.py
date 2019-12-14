from base64 import b64encode
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from nonebot import logger

from utils.customDecorators import CatchRequestsException
from utils.customObjects import convertImageFormat
from utils.exception import BotRequestError
from utils.networkUtils import NetworkUtils

from .config import Config


@CatchRequestsException(prompt='从Pixiv获取接口信息失败')
def _baseGetJSON(params: dict) -> dict:
    r = requests.get(Config.apis.address, params=params, timeout=3)
    r.raise_for_status()
    resp: dict = r.json()
    if resp.get('error'):
        reason = ''.join([str(i) for _, i in resp['error'].items()])
        raise BotRequestError(reason)
    return resp


@CatchRequestsException(prompt='下载图片失败', retries=Config.apis.retries)
def downloadImage(url: str) -> str:
    headers = {'Referer': 'https://www.pixiv.net'}
    r = requests.get(url,
                     headers=headers,
                     timeout=(6, 12),
                     proxies=NetworkUtils.proxy)
    r.raise_for_status()
    pngImage = convertImageFormat(r.content)
    return f'base64://{b64encode(pngImage).decode()}'


def downloadMutliImage(urls: list) -> dict:
    threadPool = ThreadPoolExecutor()
    resultList = list(threadPool.map(downloadImage, urls))
    return {urls[i]: resultList[i] for i in range(len(urls))}


class pixiv:
    @staticmethod
    def getRank(rankLevel: str = 'week') -> dict:
        argsPayload = {'type': 'rank', 'mode': rankLevel}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def searchIllust(keyword: str,
                     page: int = 1,
                     searchMode: int = 0,
                     ascending: bool = False) -> dict:
        searchModeString = (
            'partial_match_for_tags' if searchMode == 0 else
            'exact_match_for_tags' if searchMode == 1 else 'title_and_caption')
        argsPayload = {
            'type': 'search',
            'word': keyword,
            'mode': searchModeString,
            'page': page,
            'order': 'date_asc' if ascending else 'date_desc'
        }
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getRelatedIllust(imageID: int) -> dict:
        argsPayload = {'type': 'related', 'id': str(imageID)}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getHotTags():
        argsPayload = {'type': 'tags'}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getImageDetail(imageID: int) -> dict:
        argsPayload = {'type': 'illust', 'id': str(imageID)}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getMemberDetail(memberID: int) -> dict:
        argsPayload = {'type': 'member', 'id': str(memberID)}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getMemberIllust(memberID: int, page: int = 1) -> dict:
        argsPayload = {
            'type': 'member_illust',
            'id': str(memberID),
            'page': str(page)
        }
        getData = _baseGetJSON(argsPayload)
        return getData
