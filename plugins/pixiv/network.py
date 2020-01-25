import os
from base64 import b64encode
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, List, Tuple

import requests
from nonebot import logger
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from utils.decorators import CatchRequestsException
from utils.exception import BotRequestError
from utils.network import NetworkUtils
from utils.objects import convertImageFormat
from utils.tmpFile import tmpFile
from utils.botConfig import settings

from .config import Config

Executor = ThreadPoolExecutor(settings.THREAD_POOL_NUM)


@CatchRequestsException(prompt='从Pixiv获取接口信息失败')
def _baseGetJSON(params: dict) -> dict:
    r = requests.get(Config.apis.address, params=params, timeout=3)
    r.raise_for_status()
    resp: dict = r.json()
    if resp.get('error'):
        reason = ''.join([str(i) for _, i in resp['error'].items()])
        raise BotRequestError(reason)
    return resp


@CatchRequestsException(prompt='下载图片失败', retries=Config.apis.retries)
def downloadImage(url: str, mosaic: bool = False) -> str:
    headers = {'Referer': 'https://www.pixiv.net'}
    r = requests.get(url,
                     headers=headers,
                     timeout=(6, 12),
                     proxies=NetworkUtils.proxy)
    r.raise_for_status()
    pngImage = convertImageFormat(r.content) if not mosaic else mosaicImage(
        r.content)
    return f'base64://{b64encode(pngImage).decode()}'


def textAlign(img: bytes,
              text: str,
              font: str = './data/font.otf',
              size: int = 100,
              color: str = '#FF0000') -> bytes:
    with tmpFile() as tf:
        with open(tf, 'wb') as f:
            f.write(img)
        with Image.open(tf) as im:
            imageFont = ImageFont.truetype(font=font, size=size)
            imageWidth, imageHeight = im.size
            textWidth, textHeight = imageFont.getsize(text)
            imageDraw = ImageDraw.Draw(im)
            textCoordinate = [(imageWidth - textWidth) / 2,
                              (imageHeight - textHeight) / 2]
            imageDraw.text(xy=textCoordinate,
                           text=text,
                           fill=color,
                           font=imageFont)
            im.save(tf, 'PNG')
        with open(tf, 'rb') as f:
            fileRead = f.read()
    return fileRead


def mosaicImage(img: bytes) -> bytes:
    with tmpFile() as tf:
        with open(tf, 'wb') as f:
            f.write(img)
        with Image.open(tf) as im:
            blured = im.filter(ImageFilter.GaussianBlur(radius=10))
            blured.save(tf, 'PNG')
        with open(tf, 'rb') as f:
            fileRead = f.read()
    imageWithText = textAlign(fileRead, 'R-18')
    return convertImageFormat(imageWithText)


def downloadMutliImage(urls: list, mosaic: bool = False) -> Dict[str, bytes]:
    download = Executor.map(lambda x: downloadImage(*x),
                            [(i, mosaic) for i in urls])
    return dict(zip(urls, download))


class pixiv:
    @staticmethod
    def getRank(rankLevel: str = 'week') -> dict:
        argsPayload = {'type': 'rank', 'mode': rankLevel}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def searchIllust(keyword: str,
                     page: int = 1,
                     searchMode: int = 0,
                     ascending: bool = False) -> dict:
        searchModeString = (
            'partial_match_for_tags' if searchMode == 0 else
            'exact_match_for_tags' if searchMode == 1 else 'title_and_caption')
        argsPayload = {
            'type': 'search',
            'word': keyword,
            'mode': searchModeString,
            'page': page,
            'order': 'date_asc' if ascending else 'date_desc'
        }
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getRelatedIllust(imageID: int) -> dict:
        argsPayload = {'type': 'related', 'id': str(imageID)}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getHotTags():
        argsPayload = {'type': 'tags'}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getImageDetail(imageID: int) -> dict:
        argsPayload = {'type': 'illust', 'id': str(imageID)}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getMemberDetail(memberID: int) -> dict:
        argsPayload = {'type': 'member', 'id': str(memberID)}
        getData = _baseGetJSON(argsPayload)
        return getData

    @staticmethod
    def getMemberIllust(memberID: int, page: int = 1) -> dict:
        argsPayload = {
            'type': 'member_illust',
            'id': str(memberID),
            'page': str(page)
        }
        getData = _baseGetJSON(argsPayload)
        return getData
