from nonebot import get_bot, NoneBot
from time import sleep
import random


async def getGroupList() -> tuple:
    botObject: NoneBot = get_bot()
    groupList = await botObject.get_group_list()
    groupIDs = (r['group_id'] for r in groupList)
    return groupIDs


async def broadcast(message: str, test: list = []):
    botObject: NoneBot = get_bot()
    groupList = test if test else await getGroupList()
    for perGroup in groupList:
        await botObject.send_group_msg(group_id=perGroup, message=message)
        sleep(random.random()*5)
