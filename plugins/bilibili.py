from dataclasses import dataclass
from re import compile as compileRegexp
from time import localtime, strftime
from typing import Any, Dict, Union

import requests
from nonebot import (
    CommandSession,
    IntentCommand,
    NLPSession,
    get_bot,
    on_command,
    on_natural_language,
)
from nonebot.message import MessageSegment
from nonebot.permission import GROUP_ADMIN, SUPERUSER

from utils.decorators import CatchRequestsException, SyncToAsync
from utils.manager import PluginManager
from utils.message import processSession

REPLY_FORMAT = """{cover}
标题:“{title}”
作者:{author} (UID:{author_id})
观看链接:
http://b23.tv/av{aid}
http://b23.tv/{bid}
发布时间:{time}
视频时长:{duration}
已有:
{view}播放,{like}点赞,{share}分享,
{favorite}收藏,{coin}投币,{danmaku}弹幕"""

MATCH_BV = compileRegexp(r"BV[a-zA-Z0-9]{8,12}")
MATCH_AV = compileRegexp(r"[aA][vV](\d{1,12})")

__plugin_name__ = "bilibili"

PluginManager(__plugin_name__)
POWER_GROUP = SUPERUSER | GROUP_ADMIN


API_URL = "https://api.imjad.cn/bilibili/v2/"
APIData_T = Dict[str, Any]


class BV_AV_Utils:
    def __init__(self):
        self.table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
        self.convertR = {j: i for i, j in enumerate(self.table)}
        self.xor = 177451812
        self.add = 8728348608
        self.s = [11, 10, 3, 8, 4, 6]

    def bv2av(self, BVid: str) -> int:
        value = sum([self.convertR[BVid[self.s[i]]] * 58 ** i for i in range(6)])
        return (value - self.add) ^ self.xor

    def av2bv(self, AVid: int) -> str:
        value = (AVid ^ self.xor) + self.add
        r = list("BV1  4 1 7  ")
        for i in range(6):
            r[self.s[i]] = self.table[value // 58 ** i % 58]
        return "".join(r)


IDCoverter = BV_AV_Utils()


class BiliParser:
    @staticmethod
    def encodeTime(seconds: int) -> str:
        minutes, seconds = seconds // 60, seconds % 60
        hours, minutes = minutes // 60, minutes % 60
        return f"{hours:0>2d}:{minutes:0>2d}:{seconds:0>2d}"

    @staticmethod
    def stamp2Time(stamp: Union[int, float]) -> str:
        publishTime = localtime(float(stamp))
        return strftime("%c %z", publishTime)

    def __call__(self, data: APIData_T) -> APIData_T:
        assert not data["code"], data["msg"]
        vidData = data["data"]
        return {
            "aid": vidData["aid"],
            "bid": IDCoverter.av2bv(vidData["aid"]),
            "title": vidData["title"],
            "desc": vidData["desc"],
            "cover": MessageSegment.image(vidData["pic"]),
            "duration": self.encodeTime(vidData["duration"]),
            "time": self.stamp2Time(vidData["pubdate"]),
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


Parser = BiliParser()


@CatchRequestsException(retries=3, prompt="请求Bilibili接口失败")
def getVideoInfo(aid: int) -> APIData_T:
    r = requests.get(API_URL, params={"aid": aid})
    r.raise_for_status()
    return r.json()


@on_command("bilibili_info", aliases=("视频信息", "b站视频"))
@processSession(pluginName=__plugin_name__)
@SyncToAsync
def vidInfo(session: CommandSession):
    aid = session.state["id"]
    responseData = getVideoInfo(aid)
    try:
        parsedData = Parser(responseData)
    except:
        if session.state.get("auto", False):
            return
        else:
            raise
    return REPLY_FORMAT.format(**parsedData)


@vidInfo.args_parser
@processSession(pluginName=__plugin_name__)
@SyncToAsync
def _(session: CommandSession):
    if session.state.get("id", None):
        return
    args = session.current_arg_text.strip()
    avResult = MATCH_AV.search(args)
    bvResult = MATCH_BV.search(args)
    if avResult:
        session.state["id"] = int(avResult.group(1))
    elif bvResult:
        session.state["id"] = IDCoverter.bv2av(avResult.group())
    else:
        session.pause("请输入正确的bv号或者av号")


@on_natural_language()
@SyncToAsync
def _(session: NLPSession):
    status = PluginManager.settings(__plugin_name__, session.ctx).status
    if not status:
        return
    avResult = MATCH_AV.search(session.msg)
    bvResult = MATCH_BV.search(session.msg)
    if avResult:
        return IntentCommand(
            100, name="bilibili_info", args={"id": int(avResult.group(1)), "auto": True}
        )
    elif bvResult:
        return IntentCommand(
            100,
            name="bilibili_info",
            args={"id": IDCoverter.bv2av(bvResult.group()), "auto": True},
        )
    else:
        return


@on_command("bilibili_disable", aliases=("禁用视频信息", "关闭视频信息"), permission=POWER_GROUP)
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, session.ctx).status = False
    return "视频信息捕捉已关闭"


@on_command("bilibili_enable", aliases=("启用视频信息", "打开视频信息"), permission=POWER_GROUP)
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, session.ctx).status = True
    return "视频信息捕捉已启用"
