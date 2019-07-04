import aiohttp

from .config import *


def _getProxy() -> dict:
    if USE_PROXY:
        proxyDict = {'proxy': PROXY_ADDRESS}
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
        'timeout': aiohttp.ClientTimeout(12, 3)
    }
    requestArgument.update(_getProxy())
    for _ in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession() as reqSession:
                async with reqSession.get(**requestArgument) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                    else:
                        data = {'error': resp.status}
        except aiohttp.ClientError as e:
            print('Async Http Error:', e)
        else:
            break
    return data
