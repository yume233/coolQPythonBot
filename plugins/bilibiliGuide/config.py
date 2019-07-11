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
USEAGE = ''