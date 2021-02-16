from nonetrip import MessageSegment

from .tools import Executor, downloadImage


def _checkIsR18(tags: list) -> bool:
    for i in ("R-18", "R-18G"):
        if i in tags:
            return True
    return False


def parseSingleImage(data: dict, mosaicR18: bool = True) -> dict:
    illustData = data["illust"]

    if illustData["page_count"] == 1:
        dwlLinks = [
            {
                "large": illustData["image_urls"]["large"],
                "medium": illustData["image_urls"]["medium"],
                "square_medium": illustData["image_urls"]["medium"],
                "original": illustData["meta_single_page"]["original_image_url"],
            }
        ]
    else:
        dwlLinks = [perLink["image_urls"] for perLink in illustData["meta_pages"]]

    hotRatio = (
        (illustData["total_bookmarks"] / illustData["total_view"])
        if illustData["total_view"]
        else 0
    )

    returnData = {
        "id": illustData["id"],
        "title": illustData["title"],
        "preview_link": dwlLinks[0]["medium"],
        "preview": str(MessageSegment.image(dwlLinks[0]["medium"])),
        "author": illustData["user"]["name"],
        "author_id": illustData["user"]["id"],
        "tags": [tag["name"] for tag in illustData["tags"]],
        "date": illustData["create_date"],
        "size": illustData["page_count"],
        "download": dwlLinks,
        "view": illustData["total_view"],
        "bookmark": illustData["total_bookmarks"],
        "ratio": hotRatio,
        "type": illustData["type"],
    }

    r18Status = _checkIsR18(returnData["tags"])
    previewDownload = str(
        MessageSegment.image(
            downloadImage(returnData["preview_link"], mosaic=(mosaicR18 and r18Status))
        )
    )

    returnData.update({"r-18": r18Status, "preview": previewDownload})
    return returnData


def parseMultiImage(data: dict, mosaicR18: bool = True) -> dict:
    returnData = {
        "size": len(data["illusts"]),
        "result": list(
            Executor.map(
                lambda x: parseSingleImage(**x),
                [
                    {"data": {"illust": perData}, "mosaicR18": mosaicR18}
                    for perData in data["illusts"]
                ],
            )
        ),
    }
    return returnData
