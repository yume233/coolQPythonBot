import json
from functools import wraps
from os.path import isfile as isFileExist
from typing import Any, List, Optional
from copy import deepcopy

from nonebot import logger

from .botConfig import settings

SETTING_DIR = './data/pluginSettings.json'

_CACHE = {}
_MODIFED = True


class _SettingsIO:
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


def nameJoin(pluginName: str, *methodsName: str) -> str:
    """Splice plugin name
    
    Parameters
    ----------
    pluginName : str
        Plugin name
    
    Returns
    -------
    str
        Name of the completed plug-in
    """
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
            if _CACHE: _SettingsIO.write(_CACHE)
            _CACHE = _SettingsIO.read()
            logger.debug(f'Plugin configuration has been updated:{_CACHE}')
            _MODIFED = False
        return function(*args, **kwargs)

    return wrapper


class SingleSetting(object):
    def __init__(self, pluginName: str, type: str, id: Optional[int] = None):
        """Get settings for a plugin
        
        Parameters
        ----------
        pluginName : str
            Plugin name
        type : str
            Location type, select group or user
        id : Optional[int], optional
            The ID of the selected type, 
            the default value is called if it is empty
        """
        assert type in ('group', 'user')
        self.name, self.type = pluginName, type
        self.id = str(id) if id != None else 'default'

    @property
    @_checker
    def settings(self) -> Any:
        return deepcopy(_CACHE[self.name]['settings'][self.type].get(
            self.id, _CACHE[self.name]['settings']['default']))

    @property
    @_checker
    def status(self) -> bool:
        return deepcopy(_CACHE[self.name]['status'][self.type].get(
            self.id, _CACHE[self.name]['status']['default']))

    @settings.setter
    def settings(self, value):
        if value == self.settings: return
        global _MODIFED, _CACHE
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
    def __call__(self,
                 pluginName: str,
                 defaultStatus: Optional[bool] = True,
                 defaultSettings: Optional[Any] = {}):
        """Register a plugin
        
        Parameters
        ----------
        pluginName : str
            Plugin name
        defaultStatus : Optional[bool], optional
            Enabled by default, by default True
        defaultSettings : Optional[Any], optional
            Empty by default, by default {}
        """
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

    registerPlugin = __call__

    def _getSettings(self,
                     pluginName: str,
                     type: str,
                     id: Optional[int] = None):
        """Get settings for a certain plugin
        
        Parameters
        ----------
        pluginName : str
            Plugin name
        type : str
            Location type, select group or user
        id : Optional[int], optional
            The ID of the selected type, 
            the default value is called if it is empty
        
        Returns
        -------
        SingleSetting
            Plugin settings object
        """
        return SingleSetting(pluginName=pluginName, type=type, id=id)

    def settings(self, pluginName: str, ctx: dict) -> SingleSetting:
        """Get plugin settings automatically based on the provided `ctx` value
        
        Parameters
        ----------
        pluginName : str
            Plugin name
        ctx : dict
            ctx content
        
        Returns
        -------
        SingleSetting
            Plug-in setting object
        """
        settingsArgs = {'pluginName': pluginName}
        settingsArgs.update({
            'type': 'group',
            'id': ctx['group_id']
        } if ctx['message_type'] == 'group' else {
            'type': 'user',
            'id': ctx['user_id']
        })
        return self._getSettings(**settingsArgs)


PluginManager = _PluginManager()
