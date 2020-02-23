import json
import os
from copy import deepcopy
from typing import Any, Dict, Optional, Callable

from nonebot.command import CommandName_T
from nonebot.typing import Context_T
from ..log import logger

SETTINGS_DIR = './data/commands.json'


class _CommandSettings:
    class SingleSetting:
        def __init__(self, saveCallback: Callable[dict], setting: dict):
            self._setting = deepcopy(setting)
            self._save = saveCallback

        @property
        def data(self) -> Dict[str, Any]:
            return self._setting

        @data.setter
        def data(self, setting: dict):
            self._save(setting)

    def __init__(self):
        self._settings = {}
        if not os.path.isfile(SETTINGS_DIR):
            return
        with open(SETTINGS_DIR, 'rt', encoding='utf-8') as f:
            self._settings.update(json.load(f))

    def _store(self):
        with open(SETTINGS_DIR, 'wt', encoding='utf-8') as f:
            f.write(
                json.dumps(self._settings,
                           ensure_ascii=False,
                           sort_keys=True,
                           indent=4))

    def registerCommand(self,
                        commandName: CommandName_T,
                        settings: Optional[Dict[str, Any]] = None):
        name: str = '.'.join(commandName)
        if self._settings.get(name): return
        self._settings[name] = settings if settings else {
            'default': {},
            'groups': {},
            'users': {}
        }
        self._store()
        logger.debug(
            f'<green>{name.title()}</green> command has been registered, ' +
            f'is set to {self._settings[name]}')

    def _getSettings(self, commandName: CommandName_T, type: str,
                     id: int) -> Dict[str, Any]:
        name: str = '.'.join(commandName)
        commandSettings: Dict[str, Any] = deepcopy(self._settings[name])
        assert type in ('groups', 'users')

        def save(d: dict):
            self._settings[name][type][id] = d
            self._store()

        return self.SingleSetting(saveCallback=save,
                                  setting=commandSettings[type].get(
                                      str(id), commandSettings['default']))

    def __call__(self, commandName: CommandName_T,
                 ctx: Context_T) -> Dict[str, Any]:
        if ctx.get('group_id'):
            type = 'groups'
            id = ctx['group_id']
        else:
            type = 'users'
            id = ctx['user_id']
        return self._getSettings(commandName, type, id)


CommandSettings = _CommandSettings()