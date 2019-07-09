import time
from nonebot import MessageSegment, on_command, CommandSession

from .config import *
from .networkRequest import netease

TIME_RANGE = {}


@on_command('netease_ticket', aliases=('点歌', '听歌'))
async def neteaseTicket(session: CommandSession):
    songKeyword = session.get('keyword')
    apiResult = await netease.search(songKeyword)
    if apiResult.get('error') != None:
        session.finish('歌曲获取失败,原因:%s' % apiResult['error'])
    songResult = apiResult['result']['songs']
    if not songResult:
        session.finish('您要找的歌曲"%s"不存在' % songKeyword)
    songID = songResult[0]['id']
    songSegment = MessageSegment.music('163', songID)
    await session.send(songSegment)


@neteaseTicket.args_parser
async def _(session: CommandSession):
    global TIME_RANGE
    userQQ = str(session.ctx.get('group_id', session.ctx['user_id']))
    if TIME_RANGE.get(userQQ) != None:
        timeShift = time.time() - TIME_RANGE[userQQ]
        if timeShift < TIME_SHIFT:
            session.finish('点歌过于频繁,请%d秒后再试' % (TIME_SHIFT - timeShift))
    TIME_RANGE[userQQ] = time.time()
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('你想听什么呢?')
    session.state['keyword'] = strippedArgs