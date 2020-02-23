from typing import Dict, List

import requests

from .exceptions import BotNotFoundError
from .log import logger
from .objects.decorators import CatchRequestsException
from .settings.utils import Config


class _NetworkUtils:
    def __init__(self):
        self.configObject = Config.network

    @property
    def proxy(self) -> Dict[str, str]:
        proxySettings: dict = self.configObject.proxy
        retValue = {
            'http': proxySettings['address'],
            'https': proxySettings['address'],
            'ftp': proxySettings['address']
        } if proxySettings['enable'] else {}
        return retValue.copy()

    def shortLink(self, links: List[str]) -> Dict[str, str]:
        @CatchRequestsException(prompt='短链接因为网络连接原因生成失败', retries=3)
        def requestShortLink(link: str, params: dict) -> Dict[str, dict]:
            r = requests.get(url=link, params=params)
            r.raise_for_status()
            return r.json()

        shortenSettings: dict = self.configObject.shorten
        authSettings: dict = shortenSettings['auth']
        if authSettings.get('apikey'):
            authParam = {'signature': authSettings['apikey']}
        elif authSettings.get('username') and authSettings.get('password'):
            authParam = {
                'username': authSettings['username'],
                'password': authSettings['password']
            }
        else:
            raise BotNotFoundError('短链接API配置文件未填写')
        fullParam: dict = {
            'action': 'bulkshortener',
            'urls[]': links,
        }
        fullParam.update(authParam)
        responseData = requestShortLink(shortenSettings['address'], fullParam)
        retDict = {}
        for perURL in responseData:
            shortData = responseData[perURL]
            if shortData['statusCode'] != 200:
                retDict[perURL] = perURL
                continue
            retDict[perURL] = responseData[perURL]['shorturl']
        return retDict


NetworkUtils = _NetworkUtils()
