from base64 import b64encode
from secrets import token_bytes
from concurrent.futures.thread import ThreadPoolExecutor
import requests
import random
from utils.customDecorators import CatchRequestsException
from .config import Config


def _changeHash(origin: bytes) -> bytes:
    fileAdd = b'\x00' * 16 + token_bytes(16)
    return origin + fileAdd


@CatchRequestsException(prompt='获取图片列表出错')
def getImageList() -> list:
    params = {'limit': 100, 'page': random.randint(1, Config.send.range)}
    address = random.choice([Config.apis.konachan, Config.apis.yande])
    proxy = {
        'http': Config.proxy.address,
        'https': Config.proxy.address
    } if Config.proxy.enable else {}
    getData = requests.get(url=address,
                           params=params,
                           proxies=proxy,
                           timeout=(3, 21))
    getData.raise_for_status()
    return getData.json()


@CatchRequestsException(prompt='下载图片失败', retries=Config.apis.retries)
def downloadImage(url) -> str:
    proxy = {
        'http': Config.proxy.address,
        'https': Config.proxy.address
    } if Config.proxy.enable else {}
    r = requests.get(url, proxies=proxy, timeout=(3, 21))
    r.raise_for_status()
    resp = b64encode(_changeHash(r.content)).decode()
    return f'base64://{resp}'


def downloadMultiImage(urls: list) -> dict:
    executor = ThreadPoolExecutor()
    resultList = list(executor.map(downloadImage, urls))
    return {urls[i]: resultList[i] for i in range(len(urls))}
