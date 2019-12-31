from typing import Dict, Iterable

import requests

from utils.decorators import CatchRequestsException
from utils.network import NetworkUtils

from .config import Config


shortLink = NetworkUtils.shortLink

@CatchRequestsException(prompt='搜索图片失败', retries=Config.apis.retries)
def searchImage(imageURL: str) -> str:
    fullURL = str(Config.apis.ascii2d) + imageURL
    getResult = requests.get(fullURL, timeout=6, proxies=NetworkUtils.proxy)
    getResult.raise_for_status()
    return getResult.text
