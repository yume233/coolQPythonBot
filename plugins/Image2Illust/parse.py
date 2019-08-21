from urllib.parse import urljoin, urlparse

from lxml import etree
from nonebot import MessageSegment, logger

from .config import Config
from .network import shortLink

_ASCII2D_PARSE = urlparse(Config.apis.ascii2d)
ASCII2D_ADDRESS = f'{_ASCII2D_PARSE.scheme}://{_ASCII2D_PARSE.netloc}/'


def _url2param(url: str) -> dict:
    paramString = urlparse(url).query
    param = {}
    for perQuery in paramString.split('&'):
        if len(perQuery.split('=')) < 2: continue
        key, value = perQuery.split('=', 1)
        param[key] = value
    return param


def getCorrectInfo(originData: str) -> dict:
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
            'id': _url2param(imageLink).get('illust_id', '')
        })
    shortedLink = shortLink([i['link_source'] for i in subjectList])
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
