from .database import database
from nonebot import NoneBot


def nameJoin(originName: str, *args):
    return originName + '.' + '.'.join(args)


class _permission:
    def __init__(self):
        self.database = database()
        self.getGroup = lambda ctx: ctx.get('group_id', 0)

    def getDisable(self, ctx: dict, pluginName: str) -> bool:
        groupID: int = self.getGroup(ctx)
        return self.database.getDisable(groupID, pluginName)

    def disablePlugin(self, ctx: dict, pluginName: str):
        groupID: int = self.getGroup(ctx)
        self.database.pluginStatChange(groupID, pluginName)

    def enablePlugin(self, ctx: dict, pluginName: str):
        groupID: int = self.getGroup(ctx)
        self.database.pluginStatChange(groupID, pluginName, True)

    def getSettings(self, ctx: dict, pluginName: str, default={}):
        groupID: int = self.getGroup(ctx)
        getResult = self.database.getSettings(groupID, pluginName)
        if not getResult:
            getResult = default
        return getResult

    def applySettings(self, ctx: dict, pluginName: str, settings: dict):
        if self.getSettings(ctx, pluginName) == settings:
            return
        groupID: int = self.getGroup(ctx)
        self.database.applySettings(groupID, pluginName, settings)

    async def writeGroups(self, bot: NoneBot):
        groupList = await bot.get_group_list()
        for groupID, groupName in [(r['group_id'], r['group_name'])
                                   for r in groupList]:
            memberList = await bot.get_group_member_list(group_id=groupID)
            self.database.addGroup(groupID, groupName, memberList)

    async def writeUsers(self, bot: NoneBot):
        groupList = await bot.get_group_list()
        userDict = {}
        for groupID, groupName in [(r['group_id'], r['group_name'])
                                   for r in groupList]:
            memberList = await bot.get_group_member_list(group_id=groupID)
            for perUser in memberList:
                username = perUser['nickname']
                userID = perUser['user_id']
                userGender = perUser['sex']
                perUser['group_name'] = groupName
                if userDict.get(str(userID)) != None:
                    userDict[str(userID)]['group'].append(perUser)
                else:
                    userDict[str(userID)] = {
                        'id': userID,
                        'gender': userGender,
                        'name': username,
                        'group': [perUser]
                    }
        # with open('test.json', 'wt', encoding='utf-8') as f:
        #     import json
        #     f.write(json.dumps(userDict, ensure_ascii=False))
        userList = []
        for perMember in userDict:
            userInfo = userDict[perMember]
            userList.append({
                'userID': userInfo['id'],
                'username': userInfo['name'],
                'userGender': userInfo['gender'],
                'userGroup': userInfo['group']
            })
        self.database.batchAddUser(userList)


permission = _permission()