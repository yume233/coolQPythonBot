from secrets import token_hex
from typing import Any, Dict, Optional, Tuple, Union

from nonebot.command import CommandName_T
from nonebot.typing import Context_T

from .command.settings import CommandSettings


class CommandManager:
    def __init__(self):
        from .command import COMMANDS
        self.commands = COMMANDS

    def _fetchRealName(self, name: Union[str, CommandName_T]) -> CommandName_T:
        if name in self.commands:
            data = self.commands[name]
            realName = data.get('equal', name)
        elif isinstance(name, str):
            name: str
            name = tuple(name.split('.'))
            assert name in self.commands
            realName = name
        return realName

    def ctxToType(self, ctx: Context_T) -> Tuple[str, int]:
        if 'group_id' in ctx: return 'groups', ctx['group_id']
        else: return 'users', ctx['user_id']

    def disableCommand(self,
                       commandName: Union[CommandName_T, str],
                       ctx: Optional[Context_T] = None,
                       type: Optional[str] = None,
                       id: Optional[int] = None):
        realName = self._fetchRealName(commandName)
        if ctx: type, id = self.ctxToType(ctx)
        originSettings = CommandSettings._getSettings(realName, type, id).data
        originSettings['enabled'] = False
        CommandSettings._getSettings(realName, type, id).data = originSettings

    def enableCommand(self,
                      commandName: Union[CommandName_T, str],
                      authKey: Optional[str] = None,
                      ctx: Optional[Context_T] = None,
                      type: Optional[str] = None,
                      id: Optional[int] = None):
        realName = self._fetchRealName(commandName)
        if ctx: type, id = self.ctxToType(ctx)
        if self.commands[realName]['require_active']:
            assert authKey

        originSettings = CommandSettings._getSettings(realName, type, id).data