import os

import yaml

from .customObjects import DictOpreating

CONFIG_DIR = 'configs/config.yml'
DEFAULT_DIR = 'configs/default.config.yml'


def configLoad(path: str):
    with open(path, 'rb') as f:
        ymlLoad = yaml.safe_load(f)
    return ymlLoad if type(ymlLoad) == dict else dict()


class _configsReader:
    def __init__(self):
        assert os.path.isfile(CONFIG_DIR)
        assert os.path.isfile(DEFAULT_DIR)
        self.__config = DictOpreating.enhance(configLoad(CONFIG_DIR))
        self.__default = DictOpreating.enhance(configLoad(DEFAULT_DIR))

    def __getattr__(self, key):
        return self.__config.get(key, self.__default[key])

    def __dict__(self):
        return {
            key: DictOpreating.weaken(self.__getattr__(key))
            for key in self.__default
        }


if not os.path.isfile(CONFIG_DIR):
    with open(CONFIG_DIR, 'wb') as c, open(DEFAULT_DIR, 'rb') as d:
        c.write(d.read())
configs = _configsReader()
