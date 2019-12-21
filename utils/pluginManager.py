from functools import wraps
from typing import Any, List

from nonebot import logger

from .database import database

_CACHE = dict()
_MODIFED = True


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
        global _MODIFED
        if _MODIFED:
            global _CACHE
            _CACHE = database.listPlugin()
            logger.debug(f'Plugin Configure Updated:{_CACHE}')
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
    def cache(self) -> dict:
        global _CACHE
        return _CACHE

    @cache.setter
    def cache(self, value):
        global _CACHE
        assert type(value) == dict
        _CACHE = value

    @property
    def modifed(self) -> bool:
        global _MODIFED
        return _MODIFED

    @modifed.setter
    def modifed(self, value):
        global _MODIFED
        assert type(value) == bool
        _MODIFED = value

    @property
    @_checker
    def settings(self) -> Any:
        return self.cache[self.name]['settings'][self.type]\
            .get(self.id, self.cache[self.name]['settings']['default'])

    @property
    @_checker
    def status(self) -> bool:
        return self.cache[self.name]['status'][self.type]\
            .get(self.id, self.cache[self.name]['status']['default'])

    @settings.setter
    def settings(self, value):
        if value == self.settings: return
        self.modifed = True
        newSetting = self.cache[self.name]['settings']
        newSetting[self.type][self.id] = value
        database.writePlugin(self.name,
                             setting=newSetting,
                             status=self.cache[self.name]['status'])

    @status.setter
    def status(self, value):
        if value == self.status: return
        self.modifed = True
        newStatus = self.cache[self.name]['status']
        newStatus[self.type][self.id] = value
        database.writePlugin(self.name,
                             setting=self.cache[self.name]['settings'],
                             status=newStatus)


class _PluginManager:
    @property
    def cache(self):
        global _CACHE
        return _CACHE

    @cache.setter
    def cache(self, value):
        global _CACHE
        assert type(value) == dict
        _CACHE = value

    @property
    def modifed(self):
        global _MODIFED
        return _MODIFED

    @modifed.setter
    def modifed(self, value):
        global _MODIFED
        assert type(value) == bool
        _MODIFED = value

    @_checker
    def registerPlugin(self,
                       pluginName: str,
                       defaultStatus: bool = True,
                       defaultSettings: Any = {}):
        if self.cache.get(pluginName):
            if self.cache[pluginName]['settings']['default'] == defaultSettings and \
                self.cache[pluginName]['status']['default'] == defaultStatus:
                return
        self.modifed = True
        temp = lambda x: {'group': dict(), 'user': dict(), 'default': x}
        logger.debug(f'Register New Plugin:{pluginName},' +
                     f'Settings:{defaultSettings},Status:{defaultStatus}')
        database.writePlugin(pluginName=pluginName,
                             status=temp(defaultStatus),
                             setting=temp(defaultSettings))

    def settings(self, pluginName: str, ctx: dict) -> SingleSetting:
        sessionType = ctx['message_type'] \
            if ctx['message_type'] == 'group' else 'user'
        sessionID = ctx['group_id'] \
            if sessionType == 'group' else ctx['user_id']
        return SingleSetting(id=sessionID,
                             pluginName=pluginName,
                             type=sessionType)


manager = _PluginManager()
