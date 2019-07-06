import asyncio
import json
import queue
import threading

import cchardet
import requests
from nonebot.log import logger


class request:
    requestException = requests.RequestException

    class response(object):
        def __init__(self, data: bytes, code: int):
            self.content = data
            self.status_code = code

        def json(self):
            return json.loads(self.content)

        def text(self):
            encoding = cchardet.detect(self.content)['encoding']
            return self.content.decode(encoding)

    @staticmethod
    async def get(*args, **kwargs) -> object:
        resultQueue = queue.Queue(1)

        def basicGet(*args, **kwargs):
            logger.debug('Start Access %s' %
                         (kwargs['url'] if kwargs.get('url') else args[0]))
            try:
                with requests.get(*args, **kwargs) as resp:
                    respObject = request.response(resp.content,
                                                  resp.status_code)
            except requests.RequestException as e:
                respObject = str(e)
            resultQueue.put(respObject)

        threading.Thread(target=basicGet, args=args, kwargs=kwargs).start()
        while not resultQueue.full():
            await asyncio.sleep(1)
        getResult = resultQueue.get()
        if type(getResult) == str:
            raise request.requestException(getResult)
        return getResult

    @staticmethod
    async def post(*args, **kwargs):
        resultQueue = queue.Queue(1)

        def basicPost(*args, **kwargs):
            logger.debug('Start Access %s' %
                         (kwargs['url'] if kwargs.get('url') else args[0]))
            try:
                with requests.post(*args, **kwargs) as resp:
                    respObject = request.response(resp.content,
                                                  resp.status_code)
                    resp.raise_for_status()
            except requests.RequestException as e:
                respObject = str(e)
            resultQueue.put(respObject)

        threading.Thread(target=basicPost, args=args, kwargs=kwargs).start()
        while not resultQueue.full():
            await asyncio.sleep(.5)
        getResult = resultQueue.get()
        if type(getResult) == str:
            raise request.requestException(getResult)
        return getResult
