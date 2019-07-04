import nonebot
import config
from os import path, mkdir, getcwd
from shutil import rmtree

PLUGINS_DIR = 'plugins'
CACHE_DIR = 'cache'


def _cacheOperationg():
    if path.exists(CACHE_DIR):
        rmtree(CACHE_DIR)
    mkdir(CACHE_DIR)


if __name__ == "__main__":
    _cacheOperationg()
    nonebot.init(config)
    pluginsFullDir = path.join(getcwd(), PLUGINS_DIR)
    nonebot.load_plugins(pluginsFullDir, PLUGINS_DIR)
    nonebot.run(host='127.0.0.1', port=8000)
