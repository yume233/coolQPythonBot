from base64 import b32encode
from copy import deepcopy
from dataclasses import dataclass
from re import compile as compileRegexp
from secrets import token_bytes
from typing import Any, Dict, Optional, Tuple, Union

from nonebot.command import CommandName_T
from nonebot.typing import Context_T

from .command import getCommandInfo
from .command.settings import CommandSettings
from .exceptions import BotProgramError

_MATCH_KEY = compileRegexp(r'BOT(?:[A-Z0-9]+-)+[A-Z0-9]+')


class ChangeNotAllowed(BotProgramError):
    pass


class ChangeNotPermitted(BotProgramError):
    pass


@dataclass
class Command:
    name: CommandName_T
    enabled: bool
    permission: int
    freqency: int
    type: str
    id: int
    autoDelete: bool = False
    key: Optional[str] = None

    def applySettings(self):
        commandInfo = getCommandInfo(self.name)
        commandSetting = CommandSettings._getSettings(
            self.name,
            self.type,
            self.id,
        )
        if not commandInfo.stateChange:
            raise ChangeNotAllowed(reason='此命令设定不允许更改')
        elif commandInfo.requireKey and (not self.key):
            raise ChangeNotPermitted(reason='更改设定需要验证密钥')
        elif commandSetting.key != self.key:
            raise ChangeNotPermitted(reason='设定更改密钥错误')

        commandSetting.permission = self.permission
        commandSetting.enabled = self.enabled
        commandSetting.freqency = self.freqency
        commandSetting.autoDelete = self.autoDelete
        CommandSettings.saveSettings(commandSetting)


class CommandManager:
    def _getCommandRealName(self, name: Union[str, CommandName_T]):
        return getCommandInfo(name).name if isinstance(name, str) else name

    def ctxToType(self, ctx: Context_T) -> Tuple[str, int]:
        if 'group_id' in ctx: return 'groups', ctx['group_id']
        else: return 'users', ctx['user_id']

    def __call__(self,
                 commandName: Union[CommandName_T, str],
                 authKey: Optional[str] = None,
                 ctx: Optional[Context_T] = None,
                 type: Optional[str] = None,
                 id: Optional[int] = None) -> Command:
        if ctx: type, id = self.ctxToType(ctx)
        assert type in ('groups', 'users')
        assert isinstance(id, int)
        name = self._getCommandRealName(commandName)
        originSetting = CommandSettings._getSettings(name, type, id)
        return Command(
            name=name,
            enabled=originSetting.enabled,
            permission=originSetting.permission,
            freqency=originSetting.freqency,
            autoDelete=originSetting.autoDelete,
            key=originSetting.key,
        )


def generateKey(spliceSize: int = 5, spliceLength: int = 5):
    randomBytes = token_bytes(spliceSize * spliceLength)
    b32Bytes = ('BOT' + b32encode(randomBytes).decode()).upper()
    finalString = '-'.join(b32Bytes[i * spliceSize:(i + 1) * spliceSize]
                           for i in range(len(randomBytes) // spliceSize))
    return finalString


def findKey(text: str) -> Optional[str]:
    for line in text.splitlines():
        result = _MATCH_KEY.search(line)
        if result: break
    return result.group() if result else None
