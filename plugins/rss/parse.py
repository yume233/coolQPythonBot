from binascii import crc32
from functools import wraps
from hashlib import sha1
from time import mktime, struct_time
from typing import Callable, Iterable

from feedparser import FeedParserDict
from feedparser import parse as parseFeed
from nonetrip.log import logger
from utils.exception import BotProgramError, ExceptionProcess


def _parseTime(timeList: Iterable[int]) -> float:
    timeStructure = struct_time(tuple(timeList))
    return mktime(timeStructure)


def _generateToken(link: str) -> str:
    shaLink = sha1(link.encode()).hexdigest()
    crc32Sha = f"{crc32(shaLink.encode()):x}"
    return crc32Sha.upper()


def _avoidKeyError(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (KeyError, AttributeError):
            raise BotProgramError(
                reason="处理RSS订阅数据失败:缺失关键数据", trace=ExceptionProcess.catch()
            )

    return wrapper


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
        if parsedData.get("bozo") != 0:
            raise parsedData["bozo_exception"]
    except Exception:
        traceID = ExceptionProcess.catch()
        raise BotProgramError(reason="处理RSS订阅数据失败", trace=traceID)

    logger.debug(f"The RSS feed information is as follows: {str(parsedData)[:100]}...")

    feedInfo: dict = parsedData.feed
    returnInfo = {
        "title": feedInfo["title"],
        "subtitle": feedInfo.get("subtitle"),
        "link": feedInfo.get("link"),
        "last_update": feedInfo.get("updated"),
        "last_update_stamp": _parseTime(feedInfo.get("updated_parsed")),
        "published": feedInfo.get("published"),
        "published_stamp": _parseTime(feedInfo.get("published_parsed")),
        "version": parsedData.get("version"),
        "token": _generateToken(feedInfo["link"]),
    }

    feedContent: dict
    feedContents = [
        {
            "title": feedContent["title"],
            "link": feedContent["link"],
            "id": feedContent.get("id"),
            "published": feedContent.get("published"),
            "published_stamp": _parseTime(feedContent.get("published_parsed")),
            "author": feedContent.get("author"),
            "all_author": "/".join(i["name"] for i in feedContent.get("authors", [])),
            "summary": feedContent.get("summary"),
        }
        for feedContent in parsedData.entries
    ]

    feedContents.sort(key=lambda x: x["published_stamp"], reverse=True)

    returnInfo.update({"content": feedContents, "size": len(feedContents)})
    return returnInfo
