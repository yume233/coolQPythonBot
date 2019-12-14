import requests
from nonebot import CommandSession, on_command

from utils.configsReader import configsReader, filePath, touch
from utils.customDecorators import SyncToAsync, CatchRequestsException
from utils.messageProc import processSession
from utils.pluginManager import manager
from utils.networkUtils import NetworkUtils

CONFIG_READ = configsReader(touch(filePath(__file__, 'config.yml')),
                            filePath(__file__, 'default.yml'))

manager.registerPlugin('wikipedia')


@CatchRequestsException(prompt='从维基获取数据出错')
def getWiki(keyword: str) -> dict:
    requestParam = {
        'action': 'opensearch',
        'search': keyword,
        'format': 'json',
        'uselang': 'zh-hans'
    }
    # proxyParam = {
    #     'http': CONFIG_READ.proxy.address,
    #     'https': CONFIG_READ.proxy.address
    # } if CONFIG_READ.proxy.enable else {}
    result = requests.get(CONFIG_READ.apis.wiki,
                          params=requestParam,
                          proxies=NetworkUtils.proxy)
    result.raise_for_status()
    return result.json()


# @CatchRequestsException(prompt='生成短链接失败')
# def shortURL(urlList: list) -> dict:
#     if not urlList:
#         return {}
#     requestParam = {'source': CONFIG_READ.apis.short_key, 'url_long': urlList}
#     result = requests.get(CONFIG_READ.apis.short, params=requestParam,timeout=3)
#     result.raise_for_status()
#     return result.json()


@on_command('wikipedia', aliases=('维基搜索', '维基'))
@processSession(pluginName='wikipedia')
@SyncToAsync
def wikipedia(session: CommandSession):
    keyword = session.get('keyword')
    session.send(f'开始Wiki搜索:{keyword}')
    _, resultTitles, resultIntros, resultLinks = getWiki(keyword)
    resultShortLinks = NetworkUtils.shortLink(resultLinks)
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
@processSession
@SyncToAsync
def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('请输入搜索关键词')
    session.state['keyword'] = strippedArgs