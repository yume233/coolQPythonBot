from asyncRequest import request

from .config import *


def _getProxy() -> dict:
    if USE_PROXY:
        proxyDict = {
            'proxies': {
                'http': PROXY_ADDRESS,
                'https': PROXY_ADDRESS
            }
        }
    else:
        proxyDict = {}
    return proxyDict


async def searchAnimeByScreenshot(imageEncoded: str) -> any:
    requestAddress = API_ADDRESS + 'search'
    data = {'error': 1}
    if len(imageEncoded) >= 1024**2:
        return {'error': 413}
    requestArgument = {
        'url': requestAddress,
        'headers': {
            'Content-Type': 'application/json'
        },
        'json': {
            'image': imageEncoded
        },
        'timeout': (3, 12)
    }
    requestArgument.update(_getProxy())
    for _ in range(MAX_RETRIES):
        try:
            returnData = await request.post(**requestArgument)
            data = returnData.json()
        except request.requestException as e:
            print('Async Http Error:', e)
        else:
            break
    return data
