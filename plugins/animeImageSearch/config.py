USE_PROXY = True
PROXY_ADDRESS = 'http://127.0.0.1:1081'
API_ADDRESS = 'https://trace.moe/api/'
MAX_RETRIES = 10
RETURN_INFO_SIZE = 3
END_SYMBOL = ('结束', '-', '算了', '再见', '滚')
REPLY_FORMAT = '''
--------------
番剧名称:{anime}
英文名:{title_english}
第{episode}话{at}秒
相似度:{similarity:.2%}'''
REPLY_SUFFIX = '''
==============
API请求剩余:{limit}/{limit_ttl}s
Powered by trace.moe'''