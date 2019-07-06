import threading
from asyncio import sleep
from queue import Queue

import requests


class requestsAsync:
    @staticmethod
    async def get(*args, **kwargs) -> bytes:
        resultQueue = Queue(1)

        def basicGET(*args, **kwargs):
            with requests.get(*args, **kwargs) as resp:
                resp.raise_for_status()
                resultQueue.put(resp.content)

        threading.Thread(target=basicGET, args=args, kwargs=kwargs).start()
        while not resultQueue.full():
            await sleep(1)
        return resultQueue.get()

    @staticmethod
    async def post(*args, **kwargs) -> bytes:
        resultQueue = Queue(1)

        def basicPOST(*args, **kwargs):
            with requests.post(*args, **kwargs) as resp:
                resp.raise_for_status()
                resultQueue.put(resp.content)

        threading.Thread(target=basicPOST, args=args, kwargs=kwargs).start()
        while not resultQueue.full():
            await sleep(1)
        return resultQueue.get()
