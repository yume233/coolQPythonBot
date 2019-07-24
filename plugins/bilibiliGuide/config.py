from datetime import timedelta

API_ADDRESS = 'https://api.imjad.cn/bilibili/v2/'
TIMELINE_ADDRESS = 'https://bangumi.bilibili.com/web_api/timeline_global'
ANIME_INFO_ADDRESS = 'https://www.biliplus.com/api/bangumi'
SHORT_LINK = 'http://b23.tv'
STOP_SYMBOL = ('结束','-')
RESULT_SIZE = 3
AFFORDABLE_AUTHOR_DELTA = timedelta(days=5)
AFFORDABLE_ANIME_DELTA = timedelta(days=14)
SEARCH_ANIME_REPEAT = '''
-----------
{preview}
番剧名称:{name},ID:{id}
更新到{newest}(话)
观看链接:{link}'''
SEARCH_AUTHOR_REPEAT = '''
----------
{preview}
up主:{name},UID:{id}
等级:{level}级'''
SEARCH_ARCHIVE_REPEAT = '''
----------
{preview}
视频名称:{name},ID:{id}
作者:{author},ID:{author_id}
观看链接:{link}'''
SEARCH_PERFIX = ''
SEARCH_SUFFIX = '''
======
Powered by Biliplus/imjad API'''
ANIME_INFO_PREFIX = '''
{preview}
番剧名称:{name}({alias})
番剧简介:{info}
共{epsize}话'''
ANIME_INFO_REPEAT = '''
------
{name}-{ep_name}
{preview}
更新时间:{pubtime}
ID:{id}
观看链接:{link}'''
ANIME_INFO_SUFFIX = '''
======
Powered by Biliplus/imjad API'''
AUTHOR_INFO_PREFIX = '''
up:{name},UID:{id}
{preview}'''
AUTHOR_INFO_REPEAT = '''
------
《{name}》,ID:{id}
{preview}
更新时间:{pubtime}
分区:{reigon}
观看链接:{link}
'''
AUTHOR_INFO_SUFFIX = '''
======
Powered by Biliplus/imjad API'''
USEAGE = ''