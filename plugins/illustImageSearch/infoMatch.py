from .config import ASCII2D_ADDRESS,RETURN_SIZE,PREDOWNLOAD_PREVIEW
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
        imageTitle = perSubject.xpath('.//a[@rel][1]/text()')[0]
        imageLink = perSubject.xpath('.//a[@rel][1]/@href')[0]
        imageSource = urlparse(imageLink).netloc
        dataDict = {
            'perview_link': perviewLink,
            'title': imageTitle,
            'link_source': imageLink,
            'source': imageSource
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