import random
import time
from base64 import b64encode
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import date
from urllib.parse import urljoin

import requests
from nonebot import CommandSession, MessageSegment, on_command, scheduler, logger
from nonebot.permission import GROUP_ADMIN, SUPERUSER

from utils.decorators import CatchRequestsException, SyncToAsync
from utils.manager import PluginManager
from utils.message import processSession
from utils.objects import callModuleAPI, convertImageFormat

__plugin_name__ = 'time_reminder'

PluginManager.registerPlugin(__plugin_name__)
POWER_GROUP = GROUP_ADMIN | SUPERUSER


class daily:
    @staticmethod
    def image() -> bytes:
        @CatchRequestsException
        def requestAPI():
            dataGet = requests.get('https://cn.bing.com/HPImageArchive.aspx',
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

        return getImage(random.choice(requestAPI()['images'])['url'])

    @staticmethod
    def hitokoto() -> str:
        @CatchRequestsException(retries=3)
        def requestAPI():
            dataGet = requests.get('https://v1.hitokoto.cn/')
            dataGet.raise_for_status()
            return dataGet.json()

        return '{hitokoto}——{from}'.format(**requestAPI())


def timeTelling(*_) -> str:
    imageEncoded = f'base64://{b64encode(daily.image()).decode()}'
    message = f'{date.today()}\n' + f'{MessageSegment.image(imageEncoded)}\n' + f'{daily.hitokoto()}'
    return message


def batchSend():
    batchExecutor = ThreadPoolExecutor(8)
    tellingSet = list(
        batchExecutor.map(timeTelling, [tuple() for _ in range(10)]))
    for groupID in [i['group_id'] for i in callModuleAPI('get_group_list')]:
        if not PluginManager.settingsSpecifyGroup(__plugin_name__,groupID).status:
            continue
        callModuleAPI('send_msg',
                      params={
                          'group_id': groupID,
                          'message': random.choice(tellingSet)
                      })


@scheduler.scheduled_job('cron', day='*')
@SyncToAsync
def scheduledTiming():
    batchSend()


@on_command('test_greeting', aliases=('测试问好', ), permission=SUPERUSER)
@processSession()
@SyncToAsync
def _(session: CommandSession):
    return timeTelling(), False


@on_command('test_greeting_batch', aliases=('测试问好群发', ), permission=SUPERUSER)
@processSession()
@SyncToAsync
def _(session: CommandSession):
    batchSend()
    return '测试完成'


@on_command('enable_greeting',
            aliases=('打开问好', '启用问好'),
            permission=POWER_GROUP)
@processSession()
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, session.ctx).status = True
    return '每日问好已启用'


@on_command('disable_greeting',
            aliases=('关闭问好', '禁用问好'),
            permission=POWER_GROUP)
@processSession()
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, session.ctx).status = False
    return '每日问好已禁用'
