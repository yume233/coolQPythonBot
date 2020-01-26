from functools import wraps
from time import mktime, struct_time
from typing import Callable, Iterable

from feedparser import FeedParserDict
from feedparser import parse as parseFeed

from utils.exception import BotProgramError, CatchException


def _parseTime(timeList: Iterable[int]) -> float:
    timeStructure = struct_time(tuple(timeList))
    return mktime(timeStructure)


def _avoidKeyError(function: Callable) -> Callable:
    @wraps
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except KeyError:
            raise BotProgramError(reason='处理RSS订阅数据失败:缺失关键数据',
                                  trace=CatchException())

    return wrapper


def _cleanNoneKey(data: dict) -> dict:
    return {i: data[i] for i in data.keys() if data[i] != None}


@_avoidKeyError
def rssParser(feed: str) -> dict:
    """Functions for handling RSS pushes
    
    Parameters
    ----------
    feed : str
        Downloaded RSS file content
    
    Returns
    -------
    dict
        A dictionary containing RSS information
    
    Raises
    ------
    BotProgramError
        Thrown when RSS processing fails
    """

    try:
        parsedData: FeedParserDict = parseFeed(feed)
        if parsedData.get('bozo') != 0:
            raise parsedData['bozo_exception']
    except:
        traceID = CatchException()
        raise BotProgramError(reason='处理RSS订阅数据失败', trace=traceID)

    feedInfo: dict = parsedData.get('feed')
    returnInfo = {
        'title': feedInfo['title'],
        'subtitle': feedInfo.get('subtitle'),
        'link': feedInfo.get('link'),
        'last_update': feedInfo.get('updated'),
        'last_update_stamp': _parseTime(feedInfo.get('updated_parsed')),
        'published': feedInfo.get('published'),
        'published_stamp': _parseTime(feedInfo.get('published_parsed')),
        'version': parsedData.get('version')
    }

    feedContent: dict
    feedContents = [_cleanNoneKey({
        'title': feedContent['title'],
        'link': feedContent.get['link'],
        'id': feedContent.get('id'),
        'published': feedContent.get('published'),
        'published_stamp': \
            _parseTime(feedContent.get('published_parsed')),
        'author': feedContent.get('author'),
        'all_author': \
            '/'.join(i['name'] for i in feedContent.get('authors',[])),
        'summary': feedContent.get('summary')
    }) for feedContent in parsedData.entires]

    returnInfo.update({'content': feedContents})
    return _cleanNoneKey(returnInfo)
