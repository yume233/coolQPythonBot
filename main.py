import os

import nonebot

import config

PLUGINS_DIR = 'plugins'
CACHE_DIR = 'cache'

if __name__ == "__main__":
    nonebot.init(config)
    pluginsFullDir = os.path.join(os.getcwd(), PLUGINS_DIR)
    nonebot.load_plugins(pluginsFullDir, PLUGINS_DIR)
    nonebot.run(host='127.0.0.1', port=8000)
