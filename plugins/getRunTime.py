import time

from nonebot import CommandSession, on_command

START_RUN_TIME = time.time()


@on_command('lifespan', aliases=('运行时间', '寿命'))
async def runtime(session: CommandSession):
    nowTime = time.time()
    timeLocal = time.localtime(START_RUN_TIME)
    timeStr = time.strftime('%Y-%m-%d %H:%M:%S %z', timeLocal)
    sendMsg = '机器人已经连续运行{runtime:.3f}s\n最后一次启动在{start}'.format(
        runtime=(nowTime - START_RUN_TIME), start=timeStr)
    await session.send(sendMsg)
