from time import localtime, mktime, strftime, strptime
from urllib.parse import urljoin

from nonebot import MessageSegment

from .config import SHORT_LINK


def _shortLink(type: str, id: int) -> str:
    return urljoin(SHORT_LINK, type + str(id))


def _formatTime(timestamp: int) -> str:
    timeArray = localtime(timestamp)
    timeFormat = '%Y-%m-%d %H:%M:%S %z'
    return strftime(timeFormat, timeArray)


def _getPreview(link: str, hw: str) -> str:
    fullLink = link + '@%s.png' % hw
    return str(MessageSegment.image(fullLink))


def _autoSort(originList: list, sortKey: str = 'id') -> list:
    sortData = sorted(originList, key=lambda x: x[sortKey], reverse=True)
    return sortData


def _antiFormatTime(timeFormat: str) -> float:
    getTime = strptime(timeFormat, '%Y-%m-%d %H:%M:%S.0')
    return mktime(getTime)


class parse:
    @staticmethod
    def space(originDict: dict) -> dict:
        userData = originDict['data']
        archiveList = [{
            'preview': _getPreview(eachItem['cover'], '180h'),
            'name': eachItem['title'],
            'reigon': eachItem['tname'],
            'pubtime_stamp': eachItem['ctime'],
            'pubtime': _formatTime(eachItem['ctime']),
            'link': _shortLink(eachItem['goto'], eachItem['param']),
            'id': int(eachItem['param']),
            'play': eachItem['play'],
            'danmaku': eachItem['danmaku']
        } for eachItem in userData['archive']['item']]
        returnData = {
            'preview': _getPreview(userData['card']['face'], '180h'),
            'id': int(userData['card']['mid']),
            'name': userData['card']['name'],
            'sign': userData['card']['sign'],
            'level': userData['card']['level_info']['current_level'],
            'video': _autoSort(archiveList, sortKey='pubtime_stamp')
        }
        return returnData

    @staticmethod
    def timeline(originDict: dict) -> list:
        timelineData = originDict['result']
        getSeason = lambda perDay: [
            {
                'name': perSeason['title'],
                'preview': _getPreview(perSeason['cover'], '240w'),
                'link': _shortLink('ep', perSeason['ep_id']),
                'id': perSeason['season_id'],
                'favourite': perSeason['favourites'],
                'publish': bool(perSeason['is_published']),
                'time': perSeason['pub_time'],
                'time_format': _formatTime(perSeason['pub_ts'])
            } for perSeason in perDay['seasons']
        ]
        returnData = [{
            'date': perDay['date'],
            'date_format': _formatTime(perDay['date_ts']),
            'day': perDay['day_of_week'],
            'today': bool(perDay['is_today']),
            'season': getSeason(perDay)
        } for perDay in timelineData]
        return returnData

    @staticmethod
    def season(originDict: dict) -> dict:
        seasonData = originDict['result']
        episodeList = [{
            'preview': _getPreview(perEp, '180h'),
            'name': perEp['index_title'],
            'ep_name': perEp['index'],
            'link': _shortLink('ep', perEp['episode_id']),
            'id': int(perEp['episode_id']),
            'new': bool(int(perEp['is_new'])),
            'pubtime': perEp['update_time'],
            'pubtime_stamp': _antiFormatTime(perEp['update_time'])
        } for perEp in seasonData['episodes']]
        returnData = {
            'name': seasonData['bangumi_title'],
            'info': seasonData['evaluate'],
            'preview': _getPreview(seasonData, '240w'),
            'alias': seasonData['alias'],
            'area': seasonData['area'],
            'episode': _autoSort(episodeList, sortKey='pubtime_stamp')
        }
        returnData.update({'epsize': len(returnData['episode'])})
        return returnData

    @staticmethod
    def search(originDict: dict) -> dict:
        searchData = originDict['data']
        seasonData = [{
            'name': perSeason['title'],
            'preview': _getPreview(perSeason['cover'], '240w'),
            'link': _shortLink('ss', perSeason['param']),
            'id': int(perSeason['param']),
            'finish': bool(perSeason.get('finish')),
            'newest': perSeason['newest_season']
        } for perSeason in searchData['items'].get('season', [])]
        authorData = [{
            'name': perAuthor['title'],
            'preview': _getPreview(perAuthor['cover'], '180h'),
            'id': int(perAuthor['param']),
            'sign': perAuthor['sign'],
            'level': perAuthor['level']
        } for perAuthor in searchData['items'].get('upper', [])]
        archiveData = [{
            'name': perArchive['title'],
            'preview': _getPreview(perArchive['cover'], '180h'),
            'link': _shortLink('av', perArchive['param']),
            'id': int(perArchive['param']),
            'author': perArchive['author'],
            'author_id': perArchive['mid']
        } for perArchive in searchData['items'].get('archive', [])]
        returnData = {
            'season_size': len(seasonData),
            'archive_size': len(archiveData),
            'author_size': len(authorData),
            'seasons': seasonData,
            'authors': authorData,
            'archives': archiveData
        }
        return returnData
