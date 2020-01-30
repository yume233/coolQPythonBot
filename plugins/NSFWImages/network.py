import random
from base64 import b64encode
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, Dict, List

import requests

from utils.botConfig import settings
from utils.decorators import CatchRequestsException
from utils.network import NetworkUtils
from utils.objects import convertImageFormat

from .config import Config

_EXECUTOR = ThreadPoolExecutor(settings.THREAD_POOL_NUM)



@CatchRequestsException(prompt='获取图片列表出错')
def getImageList() -> List[Dict[str, Any]]:
    params = {'limit': 100, 'page': random.randint(1, Config.send.range)}
    address = random.choice(Config.apis.addresses)
    getData = requests.get(url=address,
                            params=params,
                            proxies=NetworkUtils.proxy,
                            timeout=6)
    getData.raise_for_status()
    return getData.json()


@CatchRequestsException(prompt='下载图片失败', retries=Config.apis.retries)
def downloadImage(url: str) -> str:
    r = requests.get(url, proxies=NetworkUtils.proxy, timeout=(3, 21))
    r.raise_for_status()
    resp = b64encode(convertImageFormat(r.content)).decode()
    return f'base64://{resp}'


def downloadMultiImage(urls: List[str]) -> Dict[str, str]:
    resultList = _EXECUTOR.map(downloadImage, sorted(urls))
    return dict(zip(urls, resultList))
