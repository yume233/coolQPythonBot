from nonebot import NoneBot, get_bot, logger

from .customDecorators import Async
from .customObjects import SyncWrapper
from .database import database


def start(bot: NoneBot):
    @bot.asgi.before_serving
    async def _():
        logger.info('Start initialization Users and Groups')
        bot: NoneBot = get_bot()
        groupList = [(i['group_id'], i['group_name'])
                     for i in await bot.get_group_list()]
        userDict = dict()
        totalMembers = list()
        for groupID, groupName in groupList:
            memberList = await bot.get_group_member_list(group_id=groupID)
            addName = lambda x: (x.update({'group_name': groupName}), x)[1]
            totalMembers.extend(map(addName, memberList))
            database.writeGroup(groupID, groupName, memberList)
            logger.debug(f'Info of Group "{groupName}"[{groupID}] Initialized')
        for perMember in totalMembers:
            username = perMember['nickname']
            userID = perMember['user_id']
            if userDict.get(str(userID)):
                userDict[str(userID)]['group'].append(perMember)
            else:
                userDict[str(userID)] = {
                    'id': userID,
                    'name': username,
                    'group': [perMember]
                }
        logger.debug(f'Users Info Initialized,Total:{len(userDict)}')
        database.batchWriteUser([
            database.writeUser(userID=userID,
                               username=userInfo['name'],
                               userGroups=userInfo['group'],
                               _inBatch=True)
            for userID, userInfo in userDict.items()
        ])
        logger.debug(f'Initialization finished!')
