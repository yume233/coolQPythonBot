from urllib.parse import urljoin, urlparse

from lxml import etree
from nonebot import MessageSegment
from nonebot.log import logger

from .config import ASCII2D_ADDRESS, PREDOWNLOAD_PREVIEW, RETURN_SIZE
from .networkRequest import createShortLink, getPreview


def _url2param(url: str) -> dict:
    paramString = urlparse(url).query
    param = {}
    for perQuery in paramString.split('&'):
        perValue = perQuery.split('=')
        if len(perValue) == 2:
            param[perValue[0]] = perValue[1]
    return param


async def getCorrectInfo(originData: str) -> dict:
    analyzeHTML = etree.HTML(originData)
    subjectList = []
    linkList = []
    for perSubject in analyzeHTML.xpath(
            '//div[@class="row item-box"][position()>1]'):
        perviewLink = urljoin(ASCII2D_ADDRESS,
                              perSubject.xpath('.//div/img/@src')[0])
        imageTitle = perSubject.xpath('.//a[@rel][1]/text()')
        imageTitle = imageTitle[0] if imageTitle else '获取失败'
        imageLink = perSubject.xpath('.//a[@rel][1]/@href')
        imageLink = imageLink[0] if imageLink else perviewLink
        imageSource = urlparse(imageLink).netloc
        imageID = _url2param(imageLink).get('illust_id','')
        dataDict = {
            'perview_link': perviewLink,
            'title': imageTitle,
            'link_source': imageLink,
            'source': imageSource,
            'id':imageID
        }
        subjectList.append(dataDict)
        linkList.append(imageLink)
    shortedLink = await createShortLink(linkList)
    returnDict = {'size': len(subjectList), 'subject': []}
    for perSubject in subjectList[:RETURN_SIZE]:
        shortLink = shortedLink[perSubject['link_source']]
        perSubject['link'] = shortLink
        perviewLink = perSubject['perview_link']
        if PREDOWNLOAD_PREVIEW:
            perviewLink = await getPreview(perviewLink)
        perSubject['perview'] = MessageSegment.image(perviewLink)
        returnDict['subject'].append(perSubject)
    return returnDict
