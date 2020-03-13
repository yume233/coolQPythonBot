from base64 import b64encode

import requests
from PIL import Image

from utils.decorators import CatchRequestsException
from utils.exception import BotProgramError
from utils.network import NetworkUtils
from utils.tmpFile import tmpFile

from .config import Config


@CatchRequestsException(prompt="下载用户发出图片失败")
def imageDownload(url: str) -> bytes:
    data = requests.get(url, timeout=(3, 6))
    data.raise_for_status()
    dataBytes = data.content
    return dataBytes


@CatchRequestsException(prompt="上传文件出错", retries=Config.api.retries)
def whatanimeUpload(file: bytes) -> dict:
    fileEncoded = b64encode(file).decode()
    params = {
        "url": Config.api.address,
        "headers": {"Content-Type": "application/json"},
        "json": {"image": fileEncoded},
        "timeout": (3, 21),
        "proxies": NetworkUtils.proxy,
    }
    data = requests.post(**params)
    data.raise_for_status()
    return data.json()


def processGIF(image: bytes) -> bytes:
    with tmpFile(ext=".gif") as file1, tmpFile(ext=".png") as file2:
        with open(file1, "wb") as f:
            f.write(image)
        with Image.open(file1) as f:
            f.save(file2, "PNG")
        with open(file2, "rb") as f:
            imageRead: bytes = f.read()
    return imageRead


def determineImageType(image: bytes) -> str:
    with tmpFile() as filename:
        with open(filename, "wb") as f:
            f.write(image)
        with Image.open(filename) as f:
            imageType: str = f.format
    return imageType.upper()
