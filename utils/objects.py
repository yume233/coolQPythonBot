from asyncio import new_event_loop
from inspect import iscoroutinefunction
from secrets import token_bytes

from nonebot import NoneBot, get_bot
from PIL import Image


def callModuleAPI(method: str, *args, **kwargs):
    from .decorators import AsyncToSync
    botObject: NoneBot = get_bot()
    AsyncInterface = botObject.__getattr__(method)
    SyncInterface = AsyncToSync(AsyncInterface)
    return SyncInterface(*args, **kwargs)


def convertImageFormat(image: bytes, quality: int = 80) -> bytes:
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
    with tmpFile() as file1, tmpFile() as file2:
        with open(file1, 'wb') as f:
            f.write(image)
        with Image.open(file1) as f:
            f.save(file2, 'BMP')
        with Image.open(file2) as f:
            f.save(file1, 'PNG', optimize=True, quality=quality)
        with open(file1, 'rb') as f:
            readData = f.read()
    return readData


class EnhancedDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DictOperating:
    @staticmethod
    def enhance(origin: dict) -> EnhancedDict:
        if type(origin) != dict:
            return origin

        def change(old: dict):
            new = EnhancedDict()
            for key, value in old.items():
                new[key] = \
                    EnhancedDict(change(value)) if type(value) == dict else value
            return new

        return change(origin)

    @staticmethod
    def weaken(origin: EnhancedDict) -> dict:
        if type(origin) != EnhancedDict:
            return origin

        def change(old: EnhancedDict):
            new = dict()
            for key, value in old.items():
                new[key] = \
                    dict(change(value)) if type(value) == EnhancedDict else value
            return new

        return change(origin)


class SyncWrapper:
    def __init__(self, subject):
        self.subject = subject

    def __getattr__(self, key: str):
        from .decorators import Sync
        origin = getattr(self.subject, key)
        if not callable(origin):
            return origin
        if not iscoroutinefunction(origin):
            return origin
        else:
            return Sync(origin)
