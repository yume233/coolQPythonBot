from .config import ASCII2D_ADDRESS
from .networkRequest import getPreview, createShortLink
from nonebot import MessageSegment
from nonebot.log import logger
from urllib.parse import urlparse, urljoin
from lxml import etree


async def getCorrectInfo(originData: str) -> dict:
    analyzeHTML = etree.HTML(originData)
    subjectList = []
    linkList = []
    for perSubject in analyzeHTML.xpath(
            '//div[@class="row item-box"][position()>1]'):
        perviewLink = urljoin(ASCII2D_ADDRESS,
                              perSubject.xpath('.//div/img/@src')[0])
        perview = MessageSegment.image(await getPreview(perviewLink))
        imageTitle = perSubject.xpath('//a[@rel][1]/text()')[0]
        imageLink = perSubject.xpath('//a[@rel][1]/@href')[0]
        imageSource = urlparse(imageLink).netloc
        dataDict = {
            'perview': perview,
            'perview_link': perviewLink,
            'title': imageTitle,
            'link_source': imageLink,
            'source': imageSource
        }
        subjectList.append(dataDict)
        linkList.append(imageLink)
    shortedLink = createShortLink(linkList)
    returnDict = {'size': len(subjectList), 'subject': []}
    for perSubject in subjectList:
        shortLink = shortedLink[perSubject['link_source']]
        perSubject['link'] = shortLink
        returnDict['subject'].append(perSubject)
    return returnDict