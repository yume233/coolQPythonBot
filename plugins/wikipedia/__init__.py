from time import time
from traceback import format_exc

import requests
from nonebot import CommandSession, on_command

from utils.configsReader import configsReader, filePath, touch
from utils.customDecorators import SyncToAsync
from utils.database import database
from utils.exception import BotRequestError
from utils.messageProc import processSession
from utils.pluginManager import manager

CONFIG_READ = configsReader(touch(filePath(__file__, 'config.yml')),
                            filePath(__file__, 'default.yml'))

manager.registerPlugin('wikipedia')


def getWiki(keyword: str) -> dict:
    requestParam = {
        'action': 'opensearch',
        'search': keyword,
        'format': 'json',
        'uselang': 'zh-hans'
    }
    proxyParam = {
        'http': CONFIG_READ.proxy.address,
        'https': CONFIG_READ.proxy.address
    } if CONFIG_READ.proxy.enable else {}
    try:
        result = requests.get(CONFIG_READ.apis.wiki,
                              params=requestParam,
                              proxies=proxyParam)
        result.raise_for_status()
    except requests.RequestException:
        traceID = database.catchException(time(), format_exc())
        raise BotRequestError('从维基拉取数据出错', traceID)
    return result.json()


def shortURL(urlList: list) -> dict:
    if not urlList:
        return {}
    requestParam = {'source': CONFIG_READ.apis.short_key, 'url_long': urlList}
    try:
        result = requests.get(CONFIG_READ.apis.short, params=requestParam)
        result.raise_for_status()
    except requests.RequestException:
        traceID = database.catchException(time(), format_exc())
        raise BotRequestError('生成短链接失败', traceID)
    return result.json()


@on_command('wikipedia', aliases=('维基搜索', '维基'))
@processSession(pluginName='wikipedia')
@SyncToAsync
def wikipedia(session: CommandSession):
    keyword = session.get('keyword')
    session.send(f'开始Wiki搜索{keyword}')
    _, resultTitles, resultIntros, resultLinks = getWiki(keyword)
    resultShortLinks = {
        i['url_long']: i['url_short']
        for i in shortURL(resultLinks)['urls']
    }
    finalResult = {'keyword': keyword, 'size': len(resultTitles)}
    finalResult['result'] = [{
        'title': resultTitles[i],
        'introduce': resultIntros[i],
        'link': resultShortLinks[resultLinks[i]]
    } for i in range(len(resultTitles))]
    repeatMessage = [
        str(CONFIG_READ.customize.repeat).format(**result)
        for result in finalResult['result']
    ]
    fullMessage = str(CONFIG_READ.customize.prefix).format(**finalResult)+\
        ''.join(repeatMessage[:CONFIG_READ.size])+\
        str(CONFIG_READ.customize.suffix).format(**finalResult)
    return fullMessage


@wikipedia.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('请输入搜索关键词')
    session.state['keyword'] = strippedArgs