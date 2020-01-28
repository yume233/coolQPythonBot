from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional

import requests

from utils.botConfig import settings
from utils.decorators import CatchRequestsException
from utils.exception import BaseBotError
from utils.manager import PluginManager
from utils.network import NetworkUtils
from utils.objects import callModuleAPI

from .config import CONFIG, __plugin_name__
from .parse import rssParser


@CatchRequestsException(prompt='获取订阅流数据失败', retries=CONFIG.refresh.retries)
def downloadFeed(url: str) -> str:
    r = requests.get(url, proxies=NetworkUtils.proxy, timeout=6)
    r.raise_for_status()
    return r.text.strip()


class RefreshFeed:
    def __init__(self, thread: Optional[int] = settings.THREAD_POOL_NUM):
        self._executor = ThreadPoolExecutor(thread)

    def _getFeed(self, feedInfo: dict) -> dict:
        returnResult = feedInfo
        try:
            feed = downloadFeed(feedInfo['address'])
            returnResult['data'] = rssParser(feed)
        except BaseBotError as e:
            returnResult['exception'] = e
        return returnResult

    def run(self):
        subscribedFeeds: List[dict] = []
        friendList: List[int] = [
            i['user_id'] for i in callModuleAPI('get_friend_list')
        ]
        groupList: List[int] = [
            i['group_id'] for i in callModuleAPI('get_group_list')
        ]
        for friend in friendList:
            for key, value in PluginManager._getSettings(
                    pluginName=__plugin_name__, type='user',
                    id=friend).settings['subscribed'].items():
                subscribedFeeds.append({
                    'type': 'user',
                    'id': friend,
                    'address': value['link'],
                    'last_update': value['last_update'],
                    'token': key
                })
        for group in groupList:
            for key, value in PluginManager._getSettings(
                    pluginName=__plugin_name__, type='group',
                    id=group).settings['subscribed'].items():
                subscribedFeeds.append({
                    'type': 'group',
                    'id': group,
                    'address': value['link'],
                    'last_update': value['last_update'],
                    'token': key
                })

        for perFeed in self._executor.map(self._getFeed, subscribedFeeds):
            feedData: dict = perFeed.get('data')
            if not feedData:
                continue
            if feedData['last_update_stamp'] <= perFeed['last_update']:
                continue
            newFeeds = [
                i for i in feedData['content']
                if i['published_stamp'] > perFeed['last_update']
            ]
            feedSettings: dict = PluginManager._getSettings(
                pluginName=__plugin_name__,
                type=perFeed['type'],
                id=perFeed['id']).settings
            feedSettings.update({
                perFeed['token']: {
                    'link': perFeed['address'],
                    'last_update': feedData['last_update_stamp']
                }
            })
            PluginManager._getSettings(
                pluginName=__plugin_name__,
                type=perFeed['type'],
                id=perFeed['id']).settings = feedSettings

            repeatMessage = '\n'.join([
                str(CONFIG.customize.subscribe_repeat).format(**i)
                for i in newFeeds[:CONFIG.customize.size]
            ])
            fullMessage = str(CONFIG.customize.subscribe_prefix).format(**feedData) \
                + f'{repeatMessage}\n' \
                + str(CONFIG.customize.subscribe_suffix).format(**feedData)

            callModuleAPI('send_msg',
                          params={
                              'group_id': perFeed['id'],
                              'message': fullMessage
                          } if perFeed['type'] == 'group' else {
                              'user_id': perFeed['id'],
                              'message': fullMessage
                          })