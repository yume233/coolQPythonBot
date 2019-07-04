API_ADDRESS = 'https://saucenao.com/search.php?output_type=2&dbmask='
PROXY_ADDRESS = 'http://127.0.0.1:1081'
MAX_RETRIES = 5
LIST_RANGE = 3
CACHE_DIR = './cache'
END_SYMBOL = ('结束', '-', '算了', '再见', '滚')
INDEX_TYPES = {
    'HentaiManga': False,
    'HentaiAnimation': False,
    'HentaiComputerGraphics': False,
    'ddbobjects': False,
    'ddbsamples': False,
    'Pixiv': True,
    'PixivHistory': True,
    'Animation': False,
    'SeigaIllust': True,
    'Danbooru': False,
    'Drawr': True,
    'Nijie': True,
    'Yande.re': False
}
INDEX_ID_LIST = {
    '5': ('pixiv', 'pixiv_id'),
    '6': ('pixivHistory', 'pixiv_id'),
    '8': ('seiga', 'seiga_id'),
    '10': ('drawr', 'drawr_id'),
    '11': ('nijie', 'nijie_id')
}
MESSAGE_FORMAT = '''
--------------
{preview}
来源:{source},ID:{id}
相似度:{simliarity:.2%}'''
MESSAGE_SUFFIX = '''
==============
共搜到{size}个结果
接口限制还有:
{shortr}/30s,{longr}/1d
'''