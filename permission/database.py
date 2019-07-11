from json import dumps, loads
from copy import deepcopy

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


class EnhancedDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(20), index=True)
    user_gender = Column(Integer)
    user_groups = Column(String, default='[]')


class Groups(Base):
    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(50), index=True)
    group_member = Column(String, default='[]')
    group_disable = Column(String, default='[]')
    group_settings = Column(String, default='{}')


class database:
    def __init__(self):
        engine = create_engine('sqlite:///res/permission.db')
        Base.metadata.create_all(engine)
        sessionFactory = sessionmaker(bind=engine)
        self.origin_session = scoped_session(sessionFactory)
        self.session = self.origin_session()


    def _addUser(self, userID: int, username: str, userGender: str,
                userGroup: list):
        enhDict = EnhancedDict()
        enhDict.user_name = str(username)[:20]
        enhDict.user_gender = 1 if userGender.lower() == 'male' else (
            2 if userGender.lower() == 'male' else 0)
        enhDict.user_groups = dumps(deepcopy(userGroup))
        baseGet = self.session.query(Users).filter_by(user_id=userID).all()
        if not baseGet:
            enhDict.user_id = userID
            baseObj = Users(**enhDict)
        else:
            baseObj: Users = baseGet[0]
            for perAttr in enhDict:
                setattr(baseObj, perAttr, enhDict[perAttr])
        return baseObj

    def addUser(self, userID: int, username: str, userGender: str,
                userGroup: list):
        baseObj = self._addUser(userID,username,userGender,userGroup)
        self.session.add(baseObj)
        self.session.commit()
    
    def batchAddUser(self,userList:list):
        baseList = [self._addUser(**perUser) for perUser in userList]
        self.session.add_all(baseList)
        self.session.commit()

    def addGroup(self, groupID: int, groupName: str, groupMember: list):
        enhDict = EnhancedDict()
        enhDict.group_name = str(groupName)[:50]
        enhDict.group_member = dumps(deepcopy(groupMember))
        baseGet = self.session.query(Groups).filter_by(group_id=groupID).all()
        if not baseGet:
            enhDict.group_id = int(groupID)
            baseObj = Groups(**enhDict)
        else:
            baseObj = baseGet[0]
            for perAttr in enhDict:
                setattr(baseObj, perAttr, enhDict[perAttr])
        self.session.add(baseObj)
        self.session.commit()

    def pluginStatChange(self,
                         groupID: int,
                         pluginName: str,
                         enable: bool = False):
        baseGet = self.session.query(Groups).filter_by(group_id=groupID).all()
        if not baseGet:
            return
        getResult: Groups = baseGet[0]
        disableList: list = loads(getResult.group_disable)
        if not enable:
            disableList.append(pluginName)
        elif pluginName in disableList:
            disableList.remove(pluginName)
        getResult.group_disable = dumps(deepcopy(disableList))
        self.session.add(getResult)
        self.session.commit()

    def applySettings(self, groupID, pluginName: str, settings: dict):
        baseGet = self.session.query(Groups).filter_by(group_id=groupID).all()
        if not baseGet:
            return {}
        getResult: Groups = baseGet[0]
        settings: dict = loads(getResult.group_settings)
        settings[pluginName] = settings
        getResult.group_settings = dumps(deepcopy(settings))
        self.session.add(getResult)
        self.session.commit()

    def getGroup(self, groupID: int) -> dict:
        baseGet = self.session.query(Groups).filter_by(group_id=groupID).all()
        if not baseGet:
            return {}
        getResult: Groups = baseGet[0]
        returnData = {
            'id': getResult.group_id,
            'name': getResult.group_name,
            'member': getResult.group_member
        }
        return returnData

    def getUser(self, userID: int) -> dict:
        baseGet = self.session.query(Users).filter_by(user_id=userID).all()
        if not baseGet:
            return {}
        getResult: Users = baseGet[0]
        returnData = {
            'id': getResult.user_id,
            'gender': getResult.user_gender,
            'name': getResult.user_name,
            'group': getResult.user_groups
        }
        return returnData

    def getSettings(self, groupID: int, pluginName: str) -> dict:
        baseGet = self.session.query(Groups).filter_by(group_id=groupID).all()
        if not baseGet:
            return {}
        getResult: Groups = baseGet[0]
        settings: dict = loads(getResult.group_settings)
        return settings.get(pluginName, {})

    def getDisable(self, groupID, pluginName: str) -> bool:
        baseGet = self.session.query(Groups).filter_by(group_id=groupID).all()
        if not baseGet:
            return False
        getResult: Groups = baseGet[0]
        disableList = loads(getResult.group_disable)
        isDisable = True if (pluginName in disableList) else False
        return isDisable
