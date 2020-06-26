from typing import Any, Dict, List, Optional

import requests

from utils.decorators import CatchRequestsException

BASE_URL = "https://bangumi.moe"


class _baseRequest:
    @staticmethod
    @CatchRequestsException(prompt="从番组获取数据失败", retries=3)
    def GET(
        url: str,
        params: Optional[Dict[str, str]] = {},
        headers: Optional[Dict[str, str]] = {},
    ) -> Any:
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    @CatchRequestsException(prompt="从番组获取数据失败", retries=3)
    def POST(
        url: str,
        data: Optional[Dict[str, Any]] = {},
        headers: Optional[Dict[str, str]] = {},
    ) -> Any:
        headers["Accept"] = "application/json"
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
        return r.json()


class _bangumi:
    @staticmethod
    def page(pageNumber: Optional[int] = 1) -> Dict[str, Any]:
        requestURL = f"{BASE_URL}/api/torrent/page/{pageNumber}"
        return _baseRequest.GET(url=requestURL)

    @staticmethod
    def searchTags(query: str) -> List[Dict[str, Any]]:
        params = {"name": query.strip(), "multi": True, "keyword": True}
        requestURL = f"{BASE_URL}/api/tag/search"
        getResult = _baseRequest.POST(url=requestURL, data=params)
        assert getResult["success"]
        return getResult["tag"] if getResult["found"] else []

    @staticmethod
    def searchBangumis(tagsID: List[str], page: Optional[int] = 1) -> Dict[str, Any]:
        params = {"tag_id": tagsID, "p": page}
        requestURL = f"{BASE_URL}/api/torrent/search"
        getResult = _baseRequest.POST(url=requestURL, data=params)
        return getResult


def _getCorrectName(subject: Dict[str, Any]) -> str:
    localeData: Dict[str, str] = subject["locale"]
    if localeData.get("zh_cn"):
        return localeData["zh_cn"]
    elif localeData.get("zh_tw"):
        return localeData["zh_tw"]
    elif localeData.get("en"):
        return localeData["en"]
    elif localeData.get("ja"):
        return localeData["ja"]
    else:
        return subject["name"]


class parseBangumi:
    @staticmethod
    def page(pageNumber: Optional[int] = 1) -> Dict[str, Any]:
        dataGet = _bangumi.page(pageNumber)
        perSubject: Dict[str, Any]
        subjectData = [
            {
                "id": perSubject["_id"],
                "name": perSubject["title"],
                "tags": perSubject["tag_ids"],
                "magnet": perSubject["magnet"],
                "hash": perSubject["infoHash"],
                "link": f'{BASE_URL}/torrent/{perSubject["_id"]}',
            }
            for perSubject in dataGet["torrents"]
        ]
        retData = {
            "total_page": dataGet["page_count"],
            "size": len(subjectData),
            "subjects": subjectData,
        }
        return retData

    @staticmethod
    def tags(query: str) -> List[Dict[str, Any]]:
        dataGet = _bangumi.searchTags(query)
        perSubject: Dict[str, Any]
        retData = [
            {
                "id": perSubject["_id"],
                "name": _getCorrectName(perSubject),
                "alias": perSubject["synonyms"],
            }
            for perSubject in dataGet
        ]
        return retData

    @staticmethod
    def search(tags: List[str], page: Optional[int] = 1) -> List[Dict[str, Any]]:
        dataGet = _bangumi.searchBangumis(tags, page)
        perSubject: Dict[str, Any]
        subjectData = [
            {
                "id": perSubject["_id"],
                "name": perSubject["title"],
                "tags": perSubject["tag_ids"],
                "magnet": perSubject["magnet"],
                "hash": perSubject["infoHash"],
                "link": f'{BASE_URL}/torrent/{perSubject["_id"]}',
            }
            for perSubject in dataGet["torrents"]
        ]
        retData = {
            "total_page": dataGet["page_count"],
            "total_size": dataGet["count"],
            "size": len(subjectData),
            "subjects": subjectData,
        }
        return retData
