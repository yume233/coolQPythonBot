import os
from base64 import b64encode
from uuid import uuid4

import aiohttp

from .config import MAX_RETRIES


async def downloadImage(url: str):
    data = b''
    timeout = aiohttp.ClientTimeout(total=12, connect=3)
    for _ in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession() as reqSession:
                async with reqSession.get(url, timeout=timeout) as resp:
                    if resp.status == 200:
                        data = await resp.read()
        except aiohttp.ClientError as e:
            print('Async Http Error:', e)
        else:
            break
    writeData = len(data)
    fileEncoded = b64encode(data).decode()
    return fileEncoded, writeData
