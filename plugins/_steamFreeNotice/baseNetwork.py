import asyncio
import queue
import threading

import requests
from nonebot.log import logger

from .config import MAX_RETRIES


class multiGet:
    def __init__(self, threadNumber: int = 1):
        self.__urlQueue = queue.Queue()
        self.__threadNum = threadNumber
        self.__resultQueue = queue.Queue()
        self.__threadLock = threading.Lock()
        self.__threadList = []

    @staticmethod
    def __networkGet(*args, **kwargs) -> dict:
        for _ in range(MAX_RETRIES):
            try:
                with requests.get(*args, **kwargs) as resp:
                    resp.raise_for_status()
                    getResult = resp.json()
            except requests.RequestException as e:
                logger.debug('Request Error:%s' % e)
                getResult = {'error': e}
        return getResult

    def __basicBehavior(self):
        while not self.__exitFlag:
            self.__threadLock.acquire()
            if not self.__urlQueue.empty():
                args, kwargs = self.__urlQueue.get()
                self.__threadLock.release()
                networkResult = self.__networkGet(*args, **kwargs)
                self.__resultQueue.put(networkResult)
            else:
                self.__threadLock.release()

    def run(self, argsList: list):
        self.__exitFlag = False
        for i in range(self.__threadNum):
            newThread = threading.Thread(
                target=self.__basicBehavior,
                name='Steam Notice Network %s' % i)
            newThread.start()
            self.__threadList.append(newThread)
        for perArg in argsList:
            self.__urlQueue.put(perArg)

    def stop(self):
        self.__exitFlag = True
        for i in self.__threadList:
            i.join()

    async def get(self):
        while not self.__urlQueue.empty():
            remain = self.__urlQueue.qsize()
            logger.debug('Session Waiting For List,remain:%s' % remain)
            await asyncio.sleep(12)
        resultList = []
        while True:
            try:
                resultList.append(self.__resultQueue.get_nowait())
            except:
                break
        return resultList
