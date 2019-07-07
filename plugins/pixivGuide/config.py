API_ADDRESS = 'https://api.imjad.cn/pixiv/v2'
IMAGE_PROXY = 'http://127.0.0.1:1081'
IMAGE_FALLBACK = 'https://i.loli.net/2019/07/06/5d204c14ae18535485.png'
MAX_RETRIES = 5
RESULT_SIZE = 3
END_SYMBOL = ('结束', '-', '算了', '再见', '滚')
ALLOW_R18 = False
GET_IMAGE_SUFFIX = '''
=========
作者:{author},ID:{author_id}
图片共{size}张
Powered by imjad API'''
GETIMAGE_PREFIX = ''
SEARCH_IMAGE_PREFIX = ''
SEARCH_IMAGE_REPEAT = '''
---------
{preview}
标题:"{title}",ID:{id}
作者:{author},ID:{author_id}'''
SEARCH_IMAGE_SUFFIX = '''
=========
此页共有{size}个结果
Powered by imjad API'''
MEMBER_IMAGE_PREFIX = ''
MEMBER_IMAGE_REPEAT = '''
---------
{preview}
标题:"{title}",ID:{id}'''
MEMBER_IMAGE_SUFFIX = '''
=========
此页共有{size}个结果
Powered by imjad API'''
RANDOM_RANK_PERFIX = '\n"{title}"-{id}\n'
RANDOM_RANK_SUFFIX = '''
作者:{author},ID:{author_id}
Powered by imjad API'''