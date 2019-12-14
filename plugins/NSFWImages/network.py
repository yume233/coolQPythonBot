import random
from base64 import b64encode
from concurrent.futures.thread import ThreadPoolExecutor

import requests

from utils.customDecorators import CatchRequestsException
from utils.customObjects import convertImageFormat
from utils.networkUtils import NetworkUtils

from .config import Config


@CatchRequestsException(prompt='获取图片列表出错')
def getImageList() -> list:
    params = {'limit': 100, 'page': random.randint(1, Config.send.range)}
    address = random.choice([Config.apis.konachan, Config.apis.yande])
    getData = requests.get(url=address,
                           params=params,
                           proxies=NetworkUtils.proxy,
                           timeout=(3, 21))
    getData.raise_for_status()
    return getData.json()


@CatchRequestsException(prompt='下载图片失败', retries=Config.apis.retries)
def downloadImage(url) -> str:
    r = requests.get(url, proxies=NetworkUtils.proxy, timeout=(3, 21))
    r.raise_for_status()
    resp = b64encode(convertImageFormat(r.content)).decode()
    return f'base64://{resp}'


def downloadMultiImage(urls: list) -> dict:
    executor = ThreadPoolExecutor()
    resultList = list(executor.map(downloadImage, urls))
    return {urls[i]: resultList[i] for i in range(len(urls))}
