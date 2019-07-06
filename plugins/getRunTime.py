from nonebot import on_command, CommandSession
import time

START_RUN_TIME = time.time()


@on_command('runtime', aliases=('运行时间', '寿命'))
async def runtime(session: CommandSession):
    nowTime = time.time()
    await session.send('机器人已经连续运行%.3fs' % (nowTime - START_RUN_TIME))
