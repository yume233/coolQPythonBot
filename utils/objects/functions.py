from typing import Any, Dict, List, Union
from nonebot import get_bot, NoneBot

APIReturn_T = Union[Dict[str, Any], List[Dict[str, Any]]]


def getObjectName(object: Any) -> str:
    if hasattr(object, '__qualname__'):
        return object.__qualname__
    elif hasattr(object, '__name__'):
        return object.__name__
    else:
        return object.__repr__()


def initiativeCallAPI(action: str, **params: Dict[str, Any]) -> APIReturn_T:
    from .decorators import AsyncToSync
    bot: NoneBot = get_bot()
    syncCaller = AsyncToSync(bot.call_action)
    return syncCaller(action, **params)