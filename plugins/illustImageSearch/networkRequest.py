import aiohttp
from .tmpFile import tmpFile
from .config import *


def _fileForm(fileRes: bytes):
    with tmpFile(path=CACHE_DIR, destory=False) as tempFilename:
        with open(tempFilename, 'wb') as f:
            f.write(fileRes)
    formData = {'file': open(tempFilename, 'rb')}
    return formData


async def uploadImage(imageRes: bytes) -> dict:
    timeout = aiohttp.ClientTimeout(10, 1.5)
    returnData = {'error': 1}
    dbMask = ''
    for perMask in INDEX_TYPES:
        dbMask = dbMask + str(int(INDEX_TYPES[perMask]))
    dbMask = str(int(dbMask, 2))
    requestAddress = API_ADDRESS + dbMask
    for _ in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession() as reqSession:
                async with reqSession.post(
                        requestAddress,
                        data=_fileForm(imageRes),
                        proxy=PROXY_ADDRESS,
                        timeout=timeout) as resp:
                    if resp.status == 200:
                        returnData = await resp.json()
                    else:
                        returnData = {'header': {'status': resp.status}}
        except aiohttp.ClientError as e:
            print('Async Http Error:', e)
        else:
            break
    return returnData


async def downloadImage(imageURL: str) -> bytes:
    async with aiohttp.ClientSession() as reqSession:
        async with reqSession.get(imageURL) as resp:
            if resp.status == 200:
                data = await resp.read()
            else:
                data = b''
    return data