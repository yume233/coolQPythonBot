import json
import os
from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from nonebot.command import CommandName_T
from nonebot.typing import Context_T

from ..log import logger

SETTINGS_DIR = './data/commands.json'
SettingLocation_T = Tuple[str, int]
SettingsDict_T = Dict[SettingLocation_T, Dict[CommandName_T, 'SingleSetting']]


@dataclass
class SingleSetting:
    name: CommandName_T
    location: SettingLocation_T
    freqency: int
    enabled: bool
    permission: str
    autoDelete: bool
    key: Optional[str] = None


class SettingsStorage:
    @staticmethod
    def read() -> SettingsDict_T:
        with open(SETTINGS_DIR, 'rt', encoding='utf-8') as f:
            settingsLoad: List[Dict[str, Any]] = json.load(f)
        settingsDict: SettingsDict_T = {}
        for i in settingsLoad:
            setting = SingleSetting(**i)
            setting.location = tuple(setting.location)
            setting.name = tuple(setting.name)
            if not setting.location in settingsDict:
                settingsDict[setting.location] = {}
            settingsDict[setting.location][setting.name] = setting
        return settingsDict

    @staticmethod
    def write(dataDict: SettingsDict_T) -> int:
        writeList: List[Dict[str, Any]] = []
        for i in dataDict.values():
            writeList.extend(j for j in i.values())
        with open(SETTINGS_DIR, 'wt', encoding='utf-8') as f:
            writeBytes = f.write(
                json.dumps(
                    writeList,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                ), )
        return writeBytes


class _CommandSettings:
    def __init__(self):
        self._settings = {}
        if not os.path.isfile(SETTINGS_DIR):
            return
        self._settings.update(SettingsStorage.read())

    def _store(self):
        SettingsStorage.write(self._settings)

    def _getSettings(self, commandName: CommandName_T, type: str,
                     id: int) -> SingleSetting:
        assert type in ('groups', 'users')
        commandLocation = type, id
        if not commandLocation in self._settings:
            return self._settings[('default', 0)][commandName]
        elif not commandName in self._settings[commandLocation]:
            return self._settings[('default', 0)][commandName]
        fetchedSettings: SingleSetting = self._settings[commandLocation][
            commandName]
        fetchedSettings.location = commandLocation
        return self._settings[commandLocation][commandName]

    def registerCommand(self, commandName: CommandName_T,
                        settings: SingleSetting):
        if commandName in self._settings[('default', 0)]: return
        settings.location = ('default', 0)
        self.saveSettings(settings)
        logger.debug(
            f'<green>{commandName}</green> command has been registered, ' +
            f'is set to {self._settings[commandName]}')

    def saveSettings(self, setting: SingleSetting):
        if not setting.location in self._settings:
            self._settings[setting.location] = {}
        self._settings[setting.location][setting.name] = setting
        self._store()

    def __call__(self, commandName: CommandName_T,
                 ctx: Context_T) -> SingleSetting:
        if ctx.get('group_id'):
            type = 'groups'
            id = ctx['group_id']
        else:
            type = 'users'
            id = ctx['user_id']
        return self._getSettings(commandName, type, id)


CommandSettings = _CommandSettings()
