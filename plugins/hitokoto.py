from time import sleep

import requests
from nonebot import CommandSession, NLPSession, on_command

from utils.customDecorators import Async
from utils.exception import BotRequestError
from utils.messageProc import processSession


@Async
def getHikotoko() -> dict:
    sleep(5)
    try:
        result = requests.get('https://v1.hitokoto.cn/')
        result.raise_for_status()
        return result.json()
    except requests.RequestException as e:
        raise Exception(e)


@on_command('hikotoko', aliases=('一言',))
@processSession
@Async
def hikotoko(session: CommandSession):
    try:
        result = requests.get('https://v1.hitokoto.cn/')
        result.raise_for_status()
        result = result.json()
    except requests.RequestException:
        raise BotRequestError
    session.send('{hitokoto}——{from}'.format(**result))
