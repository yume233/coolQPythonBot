from dataclasses import dataclass
from functools import wraps
from typing import Callable, Dict, Iterable, Union

from nonebot.command import CommandHandler_T, CommandName_T, on_command
from nonebot.permission import EVERYBODY

from ..log import logger
from .message import CommandFunction
from .settings import CommandSettings, SingleSetting


@dataclass(frozen=True)
class CommandInfo:
    name: CommandName_T
    aliases: Iterable[str]
    defaultEnabled: bool
    defaultFreqency: int
    defaultPermission: int
    stateChange: bool
    requireKey: bool


_COMMANDS: Dict[CommandName_T, CommandInfo] = {}
_ALIASES: Dict[str, CommandName_T] = {}


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

    def decorator(function: CommandHandler_T) -> CommandHandler_T:
        global _COMMANDS, _ALIASES
        if not (enabledAsDefault or allowStateChange):
            logger.warning(
                f'<green>{name}</green> command has been set to ' +
                'be disabled and can not be enabled by default, ' +
                'which means that this command will not be invoked by any means.'
            )

        _ALIASES.update({i: name for i in aliases})
        _COMMANDS[name] = CommandInfo(
            name=name,
            aliases=aliases,
            defaultEnabled=enabledAsDefault,
            defaultPermission=permission,
            defaultFreqency=defaultFreqency,
            stateChange=allowStateChange,
            requireKey=requireActivateKey,
        )

        CommandSettings.registerCommand(
            commandName=name,
            settings=SingleSetting(
                name=name,
                location=('default', 0),
                freqency=defaultFreqency,
                enabled=enabledAsDefault,
                permission=permission,
                autoDelete=autoDelete,
            ),
        )

        return CommandFunction(
            function,
            name,
            aliases=aliases,
            permission=permission,
            **kwargs,
        )

    return decorator


def getCommandInfo(name: Union[str, CommandName_T]) -> CommandInfo:
    realName = _ALIASES[name] if isinstance(name, str) else name
    return _COMMANDS[realName]
