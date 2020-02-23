import os
from typing import Any, Dict

from yaml import safe_load

from ..objects.classes import DictOperating

CONFIG_DIR = './configs/utils.yml'
DEFAULT_DIR = './configs/default/utils.yml'


def _copyFile():
    if not os.path.isfile(CONFIG_DIR):
        with open(CONFIG_DIR, 'wt', encoding='utf-8') as config, open(
                DEFAULT_DIR, 'rt', encoding='utf-8') as default:
            config.write(default.read())


_copyFile()
with open(CONFIG_DIR, 'rt', encoding='utf-8') as f:
    _configLoad = safe_load(f)
CONFIG = Config = DictOperating.enhance(_configLoad)
