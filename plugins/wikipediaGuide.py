from asyncRequest import request
from nonebot import on_command, CommandSession

WIKI_API_ADDRESS = 'https://zh.wikipedia.org/w/api.php'
PROXY_ADDRESS = 'http://127.0.0.1:1081'
RESULT_SIZE = 3
SHORT_LINK_KEY = '569452181'
SHORT_LINK_API = 'https://api.weibo.com/2/short_url/shorten.json'
MESSAGE_PREFIX = '''
您搜索的关键词为:“{keyword}”'''
MESSAGE_REPEAT = '''
-------------
标题:“{title}”
介绍:“{introduce}”
详情:{link}'''
MESSAGE_SUFFIX = '''
=============
共返回{size}个结果
Powered by Wikipedia'''


async def _getWiki(keyword: str) -> dict:
    requestParam = {
        'action': 'opensearch',
        'search': keyword,
        'format': 'json',
        'uselang': 'zh-hans'
    }
    proxyParam = {'http': PROXY_ADDRESS, 'https': PROXY_ADDRESS}
    try:
        result = await request.get(
            WIKI_API_ADDRESS, params=requestParam, proxies=proxyParam)
        result = {'result': result.json()}
    except request.requestException as e:
        result = {'error': e}
    return result


async def _shortURL(urlList: list) -> dict:
    if not urlList:
        return {}
    requestParam = {'source': SHORT_LINK_KEY, 'url_long': urlList}
    try:
        result = await request.get(SHORT_LINK_API, params=requestParam)
        result = {
            perurl['url_long']: perurl['url_short']
            for perurl in result.json()['urls']
        }
    except request.requestException as e:
        result = {'error': e}
    return result


@on_command('wikipedia_search', aliases=('维基', '搜索'))
async def wikipediaSearch(session: CommandSession):
    keyword = session.get('keyword', prompt='关键词未输入')
    await session.send('开始Wiki搜索:%s' % keyword)
    wikiResult = await _getWiki(keyword)
    if wikiResult.get('error'):
        session.finish('获取Wiki数据失败,原因:%s' % wikiResult['error'])
    resultKeywords, resultIndroduces, resultLinks = wikiResult['result'][1:]
    resultShortLinks = await _shortURL(resultLinks)
    if resultShortLinks.get('error'):
        session.finish('短链接获取失败,原因:%s' % resultShortLinks['error'])
    finalResult = {'keyword': keyword, 'size': len(resultKeywords)}
    finalResult['result'] = [{
        'title': resultKeywords[i],
        'introduce': resultIndroduces[i],
        'link': resultShortLinks[resultLinks[i]]
    } for i in range(len(resultKeywords))]
    messageRepeat = [
        MESSAGE_REPEAT.format(**result) for result in finalResult['result']
    ]
    messageFull = MESSAGE_PREFIX.format(**finalResult) + ''.join(
        messageRepeat[:RESULT_SIZE]) + MESSAGE_SUFFIX.format(**finalResult)
    await session.send(messageFull, at_sender=True)


@wikipediaSearch.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('请输入搜索关键词')
    session.state['keyword'] = strippedArgs