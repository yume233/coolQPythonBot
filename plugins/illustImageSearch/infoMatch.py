from .config import INDEX_ID_LIST
from nonebot import MessageSegment
from nonebot.log import logger

def getCorrectInfo(originData: dict) -> dict:
    dataHeader = originData['header']
    dataResult = originData['results']
    shortRemain = dataHeader['short_remaining']
    longRemain = dataHeader['long_remaining']
    resultSize = dataHeader['results_returned']
    returnHeader = {
        'shortr': shortRemain,
        'longr': longRemain,
        'size': resultSize
    }
    resultList = []
    for perResult in dataResult:
        indexID = perResult['header']['index_id']
        getType, getKey = INDEX_ID_LIST.get(str(indexID), [None, None])
        if getType == None:
            from json import dumps
            logger.debug("Can't indentify JSON:'%s'"%dumps(perResult,ensure_ascii=False))
            continue
        imageID = int(perResult['data'][getKey])
        imagePreviewLink = str(perResult['header']['thumbnail'])
        imagePreviewSegment = MessageSegment.image(file=imagePreviewLink)
        imageSimilarity = float(perResult['header']['similarity'])
        singleResult = {
            'source': getType,
            'id': imageID,
            'preview': imagePreviewSegment,
            'preview_link':imagePreviewLink,
            'simliarity': imageSimilarity / 100
        }
        resultList.append(singleResult)
    return {'header': returnHeader, 'result': resultList}
