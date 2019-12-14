import os
from typing import Union

import yaml

from .customObjects import DictOpreating


def loadConfigInYAML(path: str) -> dict:
    with open(path, 'rb') as f:
        ymlLoad = yaml.safe_load(f)
    return ymlLoad if type(ymlLoad) == dict else dict()


def filenameQuickChange(file: str, name: str) -> str:
    path, _ = os.path.split(file)
    return os.path.join(path, name)


def touchFile(path: str, newContent: Union[str, bytes] = None) -> None:
    if not os.path.isfile(path):
        if type(newContent) == bytes:
            with open(path, 'wb') as f:
                f.write(newContent)
        elif type(newContent) == str:
            with open(path, 'wt', encoding='utf-8') as f:
                f.write(newContent)
    return path


def copyFileInText(originPath: str,
                   targetPath: str,
                   encoding: str = 'utf-8') -> int:
    with open(originPath,'rt',encoding=encoding) as origin,\
        open(targetPath,'wt',encoding=encoding) as target:
        totalWrite: int = target.write(origin.read())
    return totalWrite


touch = touchFile
filePath = filenameQuickChange
configLoad = loadConfigInYAML


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
