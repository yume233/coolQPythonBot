from os.path import isfile as isFileExist
from typing import Dict, List

import requests
from nonebot import logger

from .configsReader import configsReader, copyFileInText, loadConfigInYAML
from .customDecorators import CatchRequestsException
from .exception import BotNotFoundError

CONFIG_DIR = './configs/network.yml'
DEFAULT_CONFIG_DIR = './configs/default.network.yml'


class _NetworkUtils:
    def __init__(self):
        if not isFileExist(CONFIG_DIR):
            copyFileInText(DEFAULT_CONFIG_DIR, CONFIG_DIR)
            logger.warning('Short link API is not configured.')
        self.configObject = configsReader(CONFIG_DIR, DEFAULT_CONFIG_DIR)

    @property
    def proxy(self) -> dict:
        proxySettings: dict = self.configObject.proxy
        if proxySettings['enable']:
            proxyAddr = proxySettings['address']
            retValue = {
                'http': proxyAddr,
                'https': proxyAddr,
                'ftp': proxyAddr
            }
        else:
            retValue = {}
        return retValue

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
        fullParam: dict = {'action': 'bulkshortener', 'urls[]': links}
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
