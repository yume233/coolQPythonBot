import re
import time
from datetime import timedelta

import nonebot
from nonebot import CommandSession, MessageSegment, on_command
from nonebot.log import logger

from .config import *
from .databaseSave import database as _database
from .infoParse import parse
from .networkRequest import bilibili

database = _database()
__plugin_name__ = 'bilibiliGuide'
__plugin_usage__ = USEAGE

@on_command('bilibili_subscribe', aliases=('b站关注', '关注','b站订阅','订阅'))
async def subscribe(session: CommandSession):
    subID = session.get('id')
    subType = session.get('type')
    subIDList = database.getSubscribeIDList(subType)
    nowTime = time.time()
    if not subID in subIDList:
        if not subType:
            getInfo = await bilibili.getSpace(subID)
            if getInfo.get('error') != None:
                session.finish('无法获取up主信息,原因:%s' % getInfo['error'])
            newestTime = 0
            for perArchive in parse.space(getInfo)['video']:
                if perArchive['pubtime_stamp'] > newestTime:
                    newestTime = perArchive['pubtime_stamp']
            if timedelta(seconds=(
                    nowTime - newestTime)).days > AFFORDABLE_AUTHOR_DELTA.days:
                session.finish(
                    '无法关注该up:要求必须在%s天内更新过视频' % AFFORDABLE_AUTHOR_DELTA.days)
        else:
            getInfo = await bilibili.getAnimeInfo(subID)
            if getInfo.get('error') != None:
                session.finish('无法获取番剧信息,原因%s' % getInfo['error'])
            newestTime = 0
            for perAnime in parse.season(getInfo)['episode']:
                if perAnime['pubtime_stamp'] > newestTime:
                    newestTime = perAnime['pubtime_stamp']
            if timedelta(seconds=(
                    nowTime - newestTime)).days > AFFORDABLE_ANIME_DELTA.days:
                session.finish(
                    '无法关注该番剧:要求必须在%s天内更新过' % AFFORDABLE_ANIME_DELTA.days)
    database.addNewSubscriber(subID, session.ctx, subType)
    await session.send('', at_sender=True)


@subscribe.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    keywordDict = {'用户': 0, '番剧': 1}
    if not strippedArgs:
        session.pause('请输入要关注的类型和其ID')
    for perSymbol in STOP_SYMBOL:
        if perSymbol in strippedArgs:
            session.finish('指令提前结束')
    getType = None
    for perKeyword in keywordDict:
        if perKeyword in strippedArgs:
            getType = keywordDict[perKeyword]
    if getType == None:
        session.pause('关注类型输入有误,请重新输入')
    matchedObj = re.search(r'\d+', strippedArgs)
    if not matchedObj:
        session.pause('关注ID输入有误,请重新输入')
    getID = int(matchedObj.group())
    session.state['id'] = getID
    session.state['type'] = getType


@on_command('bilibili_search', aliases=('b站搜索', ))
async def search(session: CommandSession):
    keyword = session.get('keyword')
    await session.send('开始Bilibili搜索:%s' % keyword)
    searchResult = await bilibili.search(keyword)
    if searchResult.get('error') != None:
        session.finish('搜索失败,原因:%s' % searchResult['error'])
    parsedResult = parse.search(searchResult)
    await session.send(msgPorcess(parsedResult), at_sender=True)


def msgPorcess(parsedResult: dict) -> str:
    animeRepeat = [
        SEARCH_ANIME_REPEAT.format(**perAnime)
        for perAnime in parsedResult['seasons']
    ]
    authorRepeat = [
        SEARCH_AUTHOR_REPEAT.format(**perAuthor)
        for perAuthor in parsedResult['authors']
    ]
    archiveRepeat = [
        SEARCH_ARCHIVE_REPEAT.format(**perArchive)
        for perArchive in parsedResult['archives']
    ]
    fullMessage = ''.join([
        SEARCH_PERFIX.format(**parsedResult), ''.join(
            animeRepeat[:RESULT_SIZE]), ''.join(authorRepeat[:RESULT_SIZE]),
        ''.join(archiveRepeat[:RESULT_SIZE]),
        SEARCH_SUFFIX.format(**parsedResult)
    ])
    return fullMessage


@search.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('请输入搜索关键词')
    session.state['keyword'] = strippedArgs