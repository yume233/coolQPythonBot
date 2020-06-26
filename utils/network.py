from copy import deepcopy
from typing import Dict, List

import requests

from . import UtilsConfig
from .decorators import CatchRequestsException
from .exception import BotNotFoundError


class _NetworkUtils:
    def __init__(self):
        self.configObject = UtilsConfig.network

    @property
    def proxy(self) -> Dict[str, str]:
        """Used to get the global network proxy address
        
        Returns
        -------
        dict
            Comply with the acceptable proxy address format for requests
        """
        proxySettings: dict = self.configObject.proxy
        retValue = (
            {
                "http": proxySettings["address"],
                "https": proxySettings["address"],
                "ftp": proxySettings["address"],
            }
            if proxySettings["enable"]
            else {}
        )
        return deepcopy(retValue)

    def shortLink(self, links: List[str]) -> Dict[str, str]:
        """Short link function to generate short links
        
        Parameters
        ----------
        links : List[str]
            A list of URLs to be shortened
        
        Returns
        -------
        Dict[str, str]
            Back to dictionary type, original link: short link
        
        Raises
        ------
        BotNotFoundError
            Throws when short link API settings are not written in the configuration file
        """

        @CatchRequestsException(prompt="短链接因为网络连接原因生成失败", retries=3)
        def requestShortLink(link: str, params: dict) -> Dict[str, dict]:
            r = requests.get(url=link, params=params)
            r.raise_for_status()
            return r.json()

        shortenSettings: dict = self.configObject.shorten
        authSettings: dict = shortenSettings["auth"]
        if authSettings.get("apikey"):
            authParam = {"signature": authSettings["apikey"]}
        elif authSettings.get("username") and authSettings.get("password"):
            authParam = {
                "username": authSettings["username"],
                "password": authSettings["password"],
            }
        else:
            raise BotNotFoundError("短链接API配置文件未填写")
        fullParam: dict = {
            "action": "bulkshortener",
            "urls[]": links,
        }
        fullParam.update(authParam)
        responseData = requestShortLink(shortenSettings["address"], fullParam)
        retDict = {}
        for perURL in responseData:
            shortData = responseData[perURL]
            if shortData["statusCode"] != 200:
                retDict[perURL] = perURL
                continue
            retDict[perURL] = responseData[perURL]["shorturl"]
        return retDict


NetworkUtils = _NetworkUtils()
