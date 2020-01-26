import requests
from utils.decorators import CatchRequestsException
from utils.network import NetworkUtils
from concurrent.futures.thread import ThreadPoolExecutor


@CatchRequestsException(prompt='获取订阅流数据失败', retries=3)
def downloadFeed(url: str) -> str:
    r = requests.get(url, proxies=NetworkUtils.proxy, timeout=6)
    r.raise_for_status()
    return r.text.strip()

class _feedReader:
    def __init__(self,thread:int=32):
        self._executor = ThreadPoolExecutor(thread)
    
    def __call__(self):
        pass