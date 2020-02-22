from base64 import b64encode
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import date
from itertools import cycle
from os.path import isfile
from urllib.parse import urljoin

import apscheduler
import requests
from nonebot import (CommandSession, MessageSegment, logger, on_command,
                     scheduler)
from nonebot.permission import GROUP_ADMIN, GROUP_MEMBER, SUPERUSER

from utils.configsReader import configsReader, copyFileInText
from utils.decorators import CatchRequestsException, SyncToAsync
from utils.manager import PluginManager
from utils.message import processSession
from utils.objects import callModuleAPI, convertImageFormat

__plugin_name__ = 'time_reminder'

PluginManager.registerPlugin(__plugin_name__)
POWER_GROUP = GROUP_ADMIN | SUPERUSER
CONFIG_DIR = './configs/greeting.yml'
DEFAULT_DIR = './configs/default.greeting.yml'

if not isfile(CONFIG_DIR):
    copyFileInText(DEFAULT_DIR, CONFIG_DIR)
CONFIG = configsReader(CONFIG_DIR, DEFAULT_DIR)
_IMAGE_LIST_CACHE = None


class daily:
    @staticmethod
    def image() -> dict:
        global _IMAGE_LIST_CACHE

        @CatchRequestsException
        def requestAPI():
            dataGet = requests.get(CONFIG.api.image,
                                   params={
                                       'format': 'js',
                                       'n': 10
                                   })
            dataGet.raise_for_status()
            return dataGet.json()

        @CatchRequestsException(retries=3)
        def getImage(imgLink: str):
            dataGet = requests.get(urljoin('https://cn.bing.com/', imgLink),
                                   timeout=(6, None))
            dataGet.raise_for_status()
            return convertImageFormat(dataGet.content)

        if not _IMAGE_LIST_CACHE:
            _IMAGE_LIST_CACHE = cycle(requestAPI()['images'])
        apiChoice = next(_IMAGE_LIST_CACHE)
        retData = {
            'source': apiChoice['copyright'],
            'source_link': apiChoice['copyrightlink'],
            'image': getImage(apiChoice['url']),
            'image_link': urljoin('https://cn.bing.com', apiChoice['url'])
        }
        return retData

    @staticmethod
    def hitokoto() -> dict:
        @CatchRequestsException(retries=3)
        def requestAPI():
            dataGet = requests.get(CONFIG.api.hitokoto)
            dataGet.raise_for_status()
            return dataGet.json()

        return requestAPI()


def timeTelling(*_) -> str:
    imageData = daily.image()
    imageEncoded = f'base64://{b64encode(imageData["image"]).decode()}'
    hitokotoGet = daily.hitokoto()
    messageData = {
        'hitokoto': hitokotoGet['hitokoto'],
        'hitokoto_from': hitokotoGet['from'],
        'image': MessageSegment.image(imageEncoded),
        'image_from': imageData['source'],
        'date': date.today()
    }
    return str(CONFIG.custom.format).format(**messageData)


def batchSend():
    executor = ThreadPoolExecutor(CONFIG.api.thread)
    groupsList = [i['group_id'] for i in callModuleAPI('get_group_list')]
    sendList = cycle(executor.map(timeTelling, [tuple() for _ in groupsList]))
    for groupID in groupsList:
        enabled = PluginManager._getSettings(__plugin_name__,
                                             type='group',
                                             id=groupID).status
        if not enabled:
            continue
        sendParams = {'group_id': groupID, 'message': next(sendList)}
        callModuleAPI('send_msg', params=sendParams)


@scheduler.scheduled_job('cron', day='*')
@SyncToAsync
def scheduledTiming():
    global _IMAGE_LIST_CACHE
    _IMAGE_LIST_CACHE = None
    batchSend()


@on_command('test_greeting', aliases=('今日一言', ), permission=GROUP_MEMBER)
@processSession
@SyncToAsync
def _(session: CommandSession):
    return timeTelling(), True


@on_command('enable_greeting',
            aliases=('打开问好', '启用问好'),
            permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, session.ctx).status = True
    return '每日问好已启用'


@on_command('disable_greeting',
            aliases=('关闭问好', '禁用问好'),
            permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, session.ctx).status = False
    return '每日问好已禁用'


@on_command('test_greeting_batch', aliases=('测试问好群发', ), permission=SUPERUSER)
@processSession
@SyncToAsync
def _(session: CommandSession):
    batchSend()
    return '测试完成'
