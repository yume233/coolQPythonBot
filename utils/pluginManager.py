import json
from functools import wraps
from os.path import isfile as isFileExist
from typing import Any, List

from nonebot import logger

from .botConfig import settings

SETTING_DIR = './data/pluginSettings.json'

_CACHE = {}
_MODIFED = True


class SettingsIO:
    @staticmethod
    def read() -> dict:
        if not isFileExist(SETTING_DIR):
            return {}
        with open(SETTING_DIR, 'rt', encoding='utf-8') as f:
            fileRead = f.read()
        return json.loads(fileRead)

    @staticmethod
    def write(data: dict) -> int:
        dumpedData = json.dumps(
            data, ensure_ascii=False, sort_keys=True,
            indent=4) if settings.DEBUG else json.dumps(data)
        with open(SETTING_DIR, 'wt', encoding='utf-8') as f:
            writeBytes = f.write(dumpedData)
        return writeBytes


def nameJoin(pluginName: str, *methodsName) -> str:
    def cleanDot(name: str) -> str:
        if name.startswith('.'):
            name = name[1:]
        if name.endswith('.'):
            name = name[:-1]
        return name

    methodsName: List[str] = [cleanDot(i) for i in methodsName if i]
    methodsName.insert(0, cleanDot(pluginName))
    return '.'.join(methodsName)


def _checker(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        global _MODIFED, _CACHE
        if _MODIFED:
            if _CACHE: SettingsIO.write(_CACHE)
            _CACHE = SettingsIO.read()
            logger.debug(f'Plugin configuration has been updated:{_CACHE}')
            _MODIFED = False
        return function(*args, **kwargs)

    return wrapper


class SingleSetting(object):
    def __init__(self, id: int, pluginName: str, type: str = 'group'):
        '''
        type choices: `group` or `user`
        '''
        assert type in ('group', 'user')
        self.id = str(id)
        self.name = str(pluginName)
        self.type = str(type)

    @property
    @_checker
    def settings(self) -> Any:
        return _CACHE[self.name]['settings'][self.type]\
            .get(self.id, _CACHE[self.name]['settings']['default'])

    @property
    @_checker
    def status(self) -> bool:
        return _CACHE[self.name]['status'][self.type]\
            .get(self.id, _CACHE[self.name]['status']['default'])

    @settings.setter
    def settings(self, value):
        if value == self.settings: return
        global _MODIFED
        _MODIFED = True
        _CACHE[self.name]['settings'][self.type][self.id] = value

    @status.setter
    def status(self, value):
        if value == self.status: return
        global _MODIFED, _CACHE
        _MODIFED = True
        _CACHE[self.name]['status'][self.type][self.id] = value


class _PluginManager:
    @_checker
    def registerPlugin(self,
                       pluginName: str,
                       defaultStatus: bool = True,
                       defaultSettings: Any = {}):
        global _MODIFED, _CACHE
        if _CACHE.get(pluginName):
            inCacheDefault = _CACHE[pluginName]['settings']['default']
            inCacheSetting = _CACHE[pluginName]['status']['default']
            if inCacheDefault == defaultSettings \
            and inCacheSetting == defaultStatus:
                return
        _MODIFED = True
        _CACHE.update({
            pluginName: {
                'settings': {
                    'group': {},
                    'user': {},
                    'default': defaultSettings
                },
                'status': {
                    'group': {},
                    'user': {},
                    'default': defaultStatus
                }
            }
        })
        logger.debug(f'Register a new plugin:{pluginName},' +
                     f'settings={defaultSettings},status={defaultStatus}')

    def settings(self, pluginName: str, ctx: dict) -> SingleSetting:
        sessionType = \
            ctx['message_type'] if ctx['message_type'] == 'group' else 'user'
        sessionID = \
            ctx['group_id'] if sessionType == 'group' else ctx['user_id']
        return SingleSetting(id=sessionID,
                             pluginName=pluginName,
                             type=sessionType)


try:
    if not isFileExist(SETTING_DIR):
        from .database import database
        SettingsIO.write(database.listPlugin())
except ImportError:
    logger.debug('Loading old plugin configuration from database failed')

manager = _PluginManager()
