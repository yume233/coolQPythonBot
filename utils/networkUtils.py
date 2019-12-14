from os.path import isfile as isFileExist
from typing import Dict, List

import requests

from .configsReader import configsReader, copyFileInText, loadConfigInYAML
from .customDecorators import CatchRequestsException

CONFIG_DIR = './configs/network.yml'
DEFAULT_CONFIG_DIR = './configs/default.network.yml'


class NetworkUtils:
    def __init__(self):
        if not isFileExist(CONFIG_DIR):
            copyFileInText(DEFAULT_CONFIG_DIR, CONFIG_DIR)
        self.configObject = configsReader(CONFIG_DIR, DEFAULT_CONFIG_DIR)

    @property
    def proxy(self) -> dict:
        proxySettings = self.configObject.proxy
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
        pass
