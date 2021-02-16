from asyncio import iscoroutinefunction
from os.path import getsize as getFileSize
from secrets import token_bytes
from typing import Any, Dict, List, Optional, Union

from nonetrip import NoneBot, get_bot
from nonetrip.compat import ActionFailed
from nonetrip.log import logger
from PIL import Image

MAX_IMAGE_SIZE = 4 * 1024 ** 2


class EnhancedDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DictOperating:
    @staticmethod
    def enhance(origin: dict) -> EnhancedDict:
        """Recursively convert all elements in a
        dictionary into an enhanced dictionary

        Parameters
        ----------
        origin : dict
            Original dictionary object

        Returns
        -------
        EnhancedDict
            Recursively enhanced dictionary object
        """

        def change(old: dict):
            return EnhancedDict(
                {
                    k: (EnhancedDict(change(v)) if isinstance(v, dict) else v)
                    for k, v in old.items()
                }
            )

        return change(origin) if isinstance(origin, dict) else origin

    @staticmethod
    def weaken(origin: EnhancedDict) -> dict:
        """Weaken the enhanced dictionary into a normal dictionary

        Parameters
        ----------
        origin : EnhancedDict
            Original enhanced dictionary

        Returns
        -------
        dict
            Ordinary dictionary object
        """

        def change(old: EnhancedDict):
            return {
                k: (dict(change(v)) if isinstance(v, EnhancedDict) else v)
                for k, v in old.items()
            }

        return change(origin) if isinstance(origin, EnhancedDict) else origin


class SyncWrapper:
    def __init__(self, subject):
        from .decorators import AsyncToSync

        self._subject = subject
        self._sync = AsyncToSync

    def __getattr__(self, key: str) -> Any:
        originAttr = getattr(self._subject, key)
        return self._sync(originAttr) if iscoroutinefunction(originAttr) else originAttr


def callModuleAPI(
    method: str, params: Optional[dict] = {}, ignoreError: Optional[bool] = False
) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
    """Call CQHTTP's underlying API

    Parameters
    ----------
    method : str
        The name of the method to call
    params : Optional[dict], optional
        Additional parameters for the call, by default {}

    Returns
    -------
    Callable
        The function that called the method
    """
    from .decorators import AsyncToSync

    botObject: NoneBot = get_bot()
    syncAPIMethod = AsyncToSync(botObject.call_action)
    logger.debug(
        "CQHTTP native API is being actively called, "
        + f"data: action={method}, params={str(params):.100s}"
    )
    try:
        return syncAPIMethod(method, **(params or {}))
    except ActionFailed as e:
        if ignoreError:
            return
        from .exception import BotMessageError, ExceptionProcess

        raise BotMessageError(reason=f"调用API出错,错误:{e}", trace=ExceptionProcess.catch())


def convertImageFormat(image: bytes, quality: Optional[int] = 80) -> bytes:
    """Convert picture format to solve the problem of unrecognizable pictures

    Parameters
    ----------
    image : bytes
        Read out the bytes of the image
    quality : int, optional
        Image compression quality, by default 80

    Returns
    -------
    bytes
        Returns the converted picture bytes
    """
    from .tmpFile import tmpFile

    quality = quality or 80

    with tmpFile() as file1, tmpFile() as file2:
        with open(file1, "wb") as f:
            f.write(image)
        with Image.open(file1) as f:
            f.save(file2, "BMP")
        for i in reversed(range(quality, 100, 5)):
            with Image.open(file2) as f:
                f.save(file1, "PNG", optimize=True, quality=i)
            if getFileSize(file1) <= MAX_IMAGE_SIZE:
                break
        with open(file1, "rb") as f:
            readData = f.read()
    return readData + b"\x00" * 16 + token_bytes(16)
