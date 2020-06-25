from datetime import datetime, timedelta
from time import localtime, strftime
from typing import Any, Dict, Union

import requests
from nonebot.message import MessageSegment

from utils.decorators import CatchRequestsException

API_URL = "https://api.imjad.cn/bilibili/v2/"
APIData_T = Dict[str, Any]


class IDCoverter:
    table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
    convertR = {j: i for i, j in enumerate(table)}
    xor = 177451812
    add = 8728348608
    s = [11, 10, 3, 8, 4, 6]

    @classmethod
    def bv2av(cls, BVid: str) -> int:
        value = sum([cls.convertR[BVid[cls.s[i]]] * 58 ** i for i in range(6)])
        return (value - cls.add) ^ cls.xor

    @classmethod
    def av2bv(cls, AVid: int) -> str:
        value = (AVid ^ cls.xor) + cls.add
        r = list("BV1  4 1 7  ")
        for i in range(6):
            r[cls.s[i]] = cls.table[value // 58 ** i % 58]
        return "".join(r)


class BiliParser:
    @staticmethod
    def encodeTime(seconds: int) -> str:
        return str(timedelta(seconds=seconds))

    @staticmethod
    def stamp2Time(stamp: Union[int, float]) -> str:
        publishTime = localtime(stamp)
        deltaTime = datetime.now() - datetime.fromtimestamp(stamp)
        return strftime("%Y/%m/%d %X (%Z)", publishTime) + f"({deltaTime}前)"

    @classmethod
    def parse(cls, data: APIData_T) -> APIData_T:
        assert not data["code"], data["msg"]
        vidData = data["data"]
        return {
            "aid": vidData["aid"],
            "bid": IDCoverter.av2bv(vidData["aid"]),
            "title": vidData["title"],
            "desc": vidData["desc"],
            "cover": MessageSegment.image(vidData["pic"]),
            "duration": cls.encodeTime(vidData["duration"]),
            "time": cls.stamp2Time(vidData["pubdate"]),
            "part": vidData["videos"],
            "author": vidData["owner"]["name"],
            "author_id": vidData["owner"]["mid"],
            "author_face": MessageSegment.image(vidData["owner"]["face"]),
            "view": vidData["stat"]["view"],
            "danmaku": vidData["stat"]["danmaku"],
            "share": vidData["stat"]["share"],
            "like": vidData["stat"]["share"],
            "coin": vidData["stat"]["coin"],
            "favorite": vidData["stat"]["favorite"],
        }


@CatchRequestsException(retries=3, prompt="请求Bilibili接口失败")
def getVideoInfo(aid: int) -> APIData_T:
    r = requests.get(API_URL, params={"aid": aid})
    r.raise_for_status()
    return r.json()
