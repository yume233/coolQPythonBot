from typing import Callable, Any
from asyncio import iscoroutinefunction


class SyncWrapper:
    def __init__(self, object: Any):
        from .decorators import AsyncToSync
        self._sync = AsyncToSync
        self._o = object

    def __getattr__(self, key: str) -> Any:
        attr = getattr(self._o, key)
        return self._sync(attr) if iscoroutinefunction(attr) else attr


class EnhancedDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DictOperating:
    @staticmethod
    def enhance(origin: dict) -> EnhancedDict:
        def change(old: dict):
            return EnhancedDict({
                k: (EnhancedDict(change(v)) if isinstance(v, dict) else v)
                for k, v in old.items()
            })

        return change(origin) if isinstance(origin, dict) else origin

    @staticmethod
    def weaken(origin: EnhancedDict) -> dict:
        def change(old: EnhancedDict):
            return {
                k: (dict(change(v)) if isinstance(v, EnhancedDict) else v)
                for k, v in old.items()
            }

        return change(origin) if isinstance(origin, EnhancedDict) else origin