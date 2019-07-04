import requests
import os
from uuid import uuid4
from .config import MAX_RETRIES


async def downloadImage(url: str) -> str:
    cacheFile = os.path.join('cache', uuid4().hex)
    for _ in range(MAX_RETRIES):
        try:
            req = requests.get(url, timeout=(3, None))
        except:
            continue
        if req.status_code == 200:
            data = req.content
        else:
            data = b''
    req.close()
    with open(cacheFile,'rb') as f:
        writeData = f.write(data)
    return cacheFile,writeData
