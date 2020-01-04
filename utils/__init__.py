import os
from yaml import safe_load
from typing import Any

UTILS_CONFIG_DIR = './configs/utils.yml'
UTILS_DEFAULT_DIR = './configs/default.utils.yml'


def _initUtils():
    if not os.path.exists('./data'):
        os.mkdir('./data')


def _utilsConfigReader() -> Any:
    from .configsReader import configsReader, copyFileInText
    if not os.path.isfile(UTILS_CONFIG_DIR):
        copyFileInText(UTILS_DEFAULT_DIR, UTILS_CONFIG_DIR)
    return configsReader(UTILS_CONFIG_DIR, UTILS_DEFAULT_DIR)

_initUtils()
UtilsConfig = _utilsConfigReader()