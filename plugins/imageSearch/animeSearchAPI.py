import requests
from base64 import urlsafe_b64encode
from .config import *


def _getProxy() -> dict:
    if USE_PROXY:
        proxyDict = {
            'http': PROXY_ADDRESS,
            'https': PROXY_ADDRESS,
            'ftp': PROXY_ADDRESS
        }
    else:
        proxyDict = {}
    return proxyDict


async def searchAnimeByScreenshot(imageDir: str) -> any:
    requestAddress = API_ADDRESS + 'search'
    with open(imageDir, 'rb') as f:
        imageBytes = f.read()
    encodedImage = urlsafe_b64encode(imageBytes).decode()
    if len(encodedImage) >= 1024**2:
        return {'error':413}
    for _ in range(MAX_RETRIES):
        try:
            res = requests.post(
                url=requestAddress,
                data={'image': encodedImage},
                timeout=(3, None),
                proxies=_getProxy())
        except:
            continue
        if res.status_code == 200:
            data = res.json()
            break
        else:
            data = {'error': res.status_code}
    res.close()
    return data
