import os

import nonebot

import config
from permission import permission

PLUGINS_DIR = 'plugins'
CACHE_DIR = 'cache'

if __name__ == "__main__":
    nonebot.init(config)
    botObj = nonebot.get_bot()

    @botObj.asgi.before_serving
    async def init():
        nonebot.logger.debug('Permission Function Start initialization.')
        await permission.writeGroups(botObj)
        await permission.writeUsers(botObj)
        nonebot.logger.info('Permission Function Initialized')

    pluginsFullDir = os.path.join(os.getcwd(), PLUGINS_DIR)
    nonebot.load_plugins(pluginsFullDir, PLUGINS_DIR)
    nonebot.run()
