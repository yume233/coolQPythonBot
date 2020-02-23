from functools import wraps
from typing import Any, Callable, Dict, Iterable, Union

from nonebot.command import CommandHandler_T, CommandName_T, on_command
from nonebot.permission import EVERYBODY

from ..log import logger
from .settings import CommandSettings
from .message import CommandFunction

_COMMANDS: Dict[CommandName_T, Dict[str, Any]] = {}
_SETTINGS: Dict[str, Dict[str, Any]] = {}


def withCommand(name: Union[str, CommandName_T],
                aliases: Union[str, Iterable[str]],
                enabledAsDefault: bool = True,
                allowStateChange: bool = True,
                requireActivateKey: bool = False,
                autoDelete: bool = False,
                defaultFreqency: int = 20,
                permission: int = EVERYBODY,
                **kwargs) -> Callable[CommandHandler_T]:
    aliases = aliases if isinstance(aliases, tuple) else (aliases, )
    name = name if isinstance(name, tuple) else (name, )

    def decorator(function: CommandHandler_T) -> Callable:
        strName: str = '.'.join(name)
        if not (enabledAsDefault or allowStateChange):
            logger.warning(
                f'<green>{strName.title()}</green> command has been set to ' +
                'be disabled and can not be enabled by default, ' +
                'which means that this command will not be invoked by any means.'
            )
        global _COMMANDS
        _COMMANDS[name] = {
            'aliases': aliases,
            'can_disable': allowStateChange,
            'require_active': requireActivateKey,
            'freqency': defaultFreqency,
            'enabled': enabledAsDefault,
            'permission': permission
        }
        for alias in aliases:
            _COMMANDS[alias] = {'equal': name}

        CommandSettings.registerCommand(commandName=name,
                                        settings={
                                            'freqency': defaultFreqency,
                                            'permission': permission,
                                            'enabled': enabledAsDefault,
                                            'auto_delete': autoDelete
                                        })

        return CommandFunction(function,
                               name,
                               aliases=aliases,
                               permission=permission,
                               **kwargs)

    return decorator
