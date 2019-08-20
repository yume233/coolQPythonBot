import os

import yaml

from .customObjects import DictOpreating


def configLoad(path: str) -> dict:
    with open(path, 'rb') as f:
        ymlLoad = yaml.safe_load(f)
    return ymlLoad if type(ymlLoad) == dict else dict()


def filePath(file: str, name: str) -> str:
    path, _ = os.path.split(file)
    return os.path.join(path, name)


def touch(path: str) -> str:
    if not os.path.isfile(path):
        open(path, 'wb').close()
    return path


class configsReader:
    def __init__(self, configDir: str, defaultDir: str):
        assert os.path.isfile(configDir)
        assert os.path.isfile(defaultDir)
        self.__config = DictOpreating.enhance(configLoad(configDir))
        self.__default = DictOpreating.enhance(configLoad(defaultDir))

    def __getattr__(self, key):
        return self.__config.get(key, self.__default[key])

    def __dict__(self):
        return {
            key: DictOpreating.weaken(self.__getattr__(key))
            for key in self.__default
        }
