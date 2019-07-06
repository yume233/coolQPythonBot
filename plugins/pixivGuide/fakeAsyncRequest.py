import threading
from asyncio import sleep
from queue import Queue

import requests


class requestsAsync:
    @staticmethod
    async def get(*args, **kwargs) -> bytes:
        resultQueue = Queue(1)

        def basicGET(*args, **kwargs):
            while True:
                try:
                    with requests.get(*args, **kwargs) as resp:
                        resp.raise_for_status()
                        resultQueue.put(resp.content)
                except requests.RequestException as e:
                    print('Async Http Error:',e)
                else:
                    break

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

    @staticmethod
    async def multiGet(argList: list) -> list:
        resultQueue = Queue(len(argList))

        def basicGET(*args, **kwargs):
            try:
                with requests.get(*args, **kwargs) as resp:
                    resp.raise_for_status()
                    resultQueue.put(resp.content)
            except requests.RequestException:
                resultQueue.put(None)

        for args, kwargs in argList:
            threading.Thread(target=basicGET, args=args, kwargs=kwargs).start()
        while not resultQueue.full():
            await sleep(1)
        resultList = []
        while not resultQueue.empty():
            getResult = resultQueue.get()
            if getResult:
                resultList.append(resultQueue.get())
        return resultList
