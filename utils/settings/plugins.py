import os
from typing import Any, Dict

from yaml import safe_load

from ..log import logger
from ..objects.classes import DictOperating

CONFIG_DIR = './configs/plugins'
DEFAULT_DIR = './configs/default'

Settings_T = Dict[str, Any]

if not os.path.exists(CONFIG_DIR):
    os.mkdir(CONFIG_DIR)


def _loadConfig(filePath: str) -> Settings_T:
    with open(filePath, 'rt', encoding='utf-8') as f:
        load = safe_load(f)
    return load if isinstance(load) else {}


def _loadAllConfig(path: str) -> Dict[str, Settings_T]:
    config = {}
    for configFile in os.listdir(path):
        _, file = os.path.split(configFile)
        file, ext = os.path.splitext(file)
        if ext != '.yml': continue
        configLoaded = _loadConfig(configFile)
        config[file] = configLoaded
        logger.trace(f'The configuration file {configFile} has been read, ' +
                     f'and the content is: {configLoaded}')
    return config


def _saveAllConfig(configs: Dict[str, Settings_T]) -> int:
    totalWriteBytes = 0
    for name in configs.keys():
        configPath = os.path.join(CONFIG_DIR, f'{name}.yml')
        defaultPath = os.path.join(DEFAULT_DIR, f'{name}.yml')
        if os.path.isfile(configPath): continue
        with open(configPath, 'wt', encoding='utf-8') as config, open(
                defaultPath, 'rt', encoding='utf-8') as default:
            totalWriteBytes += config.write(default.read())
    return totalWriteBytes


class _PluginsConfigs:
    def __init__(self):
        self._default = _loadAllConfig(DEFAULT_DIR)
        self._config = _loadAllConfig(CONFIG_DIR)
        _saveAllConfig(self._default)

    def __call__(self, name: str):
        config = self._config.get(name, self._default[name])
        return DictOperating.enhance(config)


PluginsConfigs = _PluginsConfigs()
