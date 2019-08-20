from time import sleep

import requests
from nonebot import CommandSession, NLPSession, on_command

from utils.customDecorators import Async
from utils.exception import BotRequestError
from utils.messageProc import processSession
from utils.pluginManager import manager

manager.registerPlugin('hitokoto')


@Async
def getHikotoko() -> dict:
    sleep(5)
    try:
        result = requests.get('https://v1.hitokoto.cn/')
        result.raise_for_status()
        return result.json()
    except requests.RequestException as e:
        raise Exception(e)


@on_command('hitokoto', aliases=('一言', ))
@processSession(pluginName='hitokoto')
@Async
def hitokoto(session: CommandSession):
    try:
        result = requests.get('https://v1.hitokoto.cn/')
        result.raise_for_status()
        result = result.json()
    except requests.RequestException:
        raise BotRequestError
    return '{hitokoto}——{from}'.format(**result), False
