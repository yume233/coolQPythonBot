from inspect import iscoroutinefunction
from typing import Optional

from nonebot import NoneBot, get_bot
from PIL import Image


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
            return EnhancedDict({
                k: (EnhancedDict(change(v)) if isinstance(v, dict) else v)
                for k, v in old.items()
            })

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

    def __getattr__(self, key: str):
        originAttr = getattr(self._subject, key)
        if iscoroutinefunction(originAttr):
            return self._sync(originAttr)
        else:
            return originAttr


def callModuleAPI(method: str, params: Optional[dict] = {}):
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
    AsyncAPIMethod = botObject.__getattr__(item=method)
    assert AsyncAPIMethod
    return AsyncToSync(AsyncAPIMethod)(**params)


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
