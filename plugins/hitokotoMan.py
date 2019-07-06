import aiohttp
from nonebot import (CommandSession, IntentCommand, NLPSession, on_command,
                     on_natural_language)

from asyncRequest import request

API_ADDRESS = 'https://v1.hitokoto.cn/'
MESSAGE_FORMAT = '{hitokoto}——{from}'


@on_command('hikotoko', aliases=('一言', '一言哥', 'sectence'))
async def hikotoko(session: CommandSession):
    gotData = await getHikotoko()
    if gotData.get('error'):
        returnMsg = '一言获取失败,错误码:%s' % gotData['error']
    else:
        returnMsg = MESSAGE_FORMAT.format(**gotData)
    await session.send(returnMsg)


@on_natural_language(keywords=('一言哥'))
async def _(session: NLPSession):
    return IntentCommand(90.0, 'hikotoko')


async def getHikotoko() -> dict:
    result = await request.get(API_ADDRESS)
    if result.status_code == 200:
        respData = result.json()
    else:
        respData = {'error': result.status_code}
    return respData
