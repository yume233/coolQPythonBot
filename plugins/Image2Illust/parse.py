from re import compile as compileRegexp
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse

import requests
from lxml import etree
from nonebot import MessageSegment, logger

from utils.decorators import CatchRequestsException
from utils.network import NetworkUtils

from .config import Config

ASCII2D_ADDRESS = f'{_ASCII2D_PARSE.scheme}://{_ASCII2D_PARSE.netloc}/'

_ASCII2D_PARSE = urlparse(Config.apis.ascii2d)
_MATCH_NUMBER = compileRegexp(r'\d{4,20}')


@CatchRequestsException(prompt='搜索图片失败', retries=Config.apis.retries)
def searchImage(imageURL: str) -> str:
    fullURL = str(Config.apis.ascii2d) + imageURL
    getResult = requests.get(fullURL, timeout=6, proxies=NetworkUtils.proxy)
    getResult.raise_for_status()
    return getResult.text


def _getNumbers(match: str) -> Optional[int]:
    searchResult = _MATCH_NUMBER.search(match)
    return None if not searchResult else int(searchResult.group(1))


def getCorrectInfo(originData: str) -> Dict[str, Any]:
    subjectList = []
    for perSubject in etree.HTML(originData).xpath\
    ('//div[@class="row item-box"][position()>1]'):
        previewLink = urljoin(ASCII2D_ADDRESS,
                              perSubject.xpath('.//div/img/@src')[0])
        imageTitle = perSubject.xpath('.//a[@rel][1]/text()')
        imageTitle = imageTitle[0] if imageTitle else '获取失败'
        imageLink = perSubject.xpath('.//a[@rel][1]/@href')
        imageLink = imageLink[0] if imageLink else previewLink
        subjectList.append({
            'preview_link': previewLink,
            'title': imageTitle,
            'link_source': imageLink,
            'source': urlparse(imageLink).netloc,
            'id': _getNumbers(imageLink)
        })
    shortedLink = NetworkUtils.shortLink(
        [i['link_source'] for i in subjectList])
    returnDict = {'size': len(subjectList), 'subject': []}
    for perSubject in subjectList:
        perSubject.update({
            'link':
            shortedLink[perSubject['link_source']],
            'preview':
            MessageSegment.image(perSubject['preview_link'])
        })
        returnDict['subject'].append(perSubject)
    return returnDict
