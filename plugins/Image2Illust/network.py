from typing import Dict, Iterable

import requests

from utils.customDecorators import CatchRequestsException

from .config import Config

PROXY = {
    'http': Config.proxy.address,
    'https': Config.proxy.address
} if Config.proxy.enable else {}


@CatchRequestsException(prompt='搜索图片失败', retries=Config.apis.retries)
def searchImage(imageURL: str) -> str:
    fullURL = str(Config.apis.ascii2d) + imageURL
    getResult = requests.get(fullURL, timeout=6, proxies=PROXY)
    getResult.raise_for_status()
    return getResult.text


@CatchRequestsException(prompt='创建短链接失败')
def shortLink(linkList: Iterable) -> Dict[str, str]:
    urlParams = {
        'source': str(Config.apis.short_key),
        'url_long': list(linkList)
    }
    apiGet = requests.get(Config.apis.short, params=urlParams,timeout=3)
    apiGet.raise_for_status()
    return {i['url_long']: i['url_short'] for i in apiGet.json()['urls']}
