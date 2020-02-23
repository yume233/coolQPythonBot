from functools import wraps
from typing import Any, Callable, Dict, Iterable, Union

from nonebot.command import CommandHandler_T, CommandName_T, on_command
from nonebot.permission import EVERYBODY

_COMMANDS: Dict[CommandName_T, Dict[str, Any]] = {}


def withCommand(name: Union[str, CommandName_T],
                aliases: Union[str, Iterable[str]],
                canDisable: bool = True,
                requireActivateKey: bool = False,
                defaultFreqency: int = 20,
                permission: int = EVERYBODY,
                **kwargs) -> Callable[CommandHandler_T]:
    def decorator(function: CommandHandler_T) -> Callable:
        @wraps(function)
        def wrapper(*args, **kwargs) -> Any:
            pass

        return wrapper

    return decorator
