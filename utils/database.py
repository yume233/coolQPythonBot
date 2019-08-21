from json import dumps, loads
from secrets import token_hex
from typing import Any, Dict, Iterator, List

from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from .botConfig import settings
from .customObjects import EnhancedDict
from .exception import BotNotFoundError

Base = declarative_base()


class Plugins(Base):
    __tablename__ = 'plugins'
    plugin_name = Column(String, primary_key=True)
    plugin_status = Column(String, default='{}')
    plugin_settings = Column(String, default='{}')


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String, index=True)
    user_groups = Column(String, default='{}')


class Groups(Base):
    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True)
    group_name = Column(String, index=True)
    group_member = Column(String)


class Errors(Base):
    __tablename__ = 'exceptions'
    exception_id = Column(Integer, primary_key=True)
    exception_trace_id = Column(Integer, unique=True, index=True)
    exception_time = Column(Float, index=True)
    exception_stack = Column(String)


class _database:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_ADDRESS,
                                    echo=settings.DATABASE_DEBUG)
        Base.metadata.create_all(self.engine)
        self.sessionFactory = sessionmaker(bind=self.engine)
        self.originSession = scoped_session(self.sessionFactory)

    def catchException(self, time: float, stack: str) -> str:
        localSession: Session = self.originSession()
        traceID = token_hex(4)
        enhDict: Errors = EnhancedDict()
        enhDict.exception_trace_id = int(traceID, 16)
        enhDict.exception_time = float(time)
        enhDict.exception_stack = stack
        localSession.add(Errors(**enhDict))
        localSession.commit()
        self.originSession.remove()
        return traceID.upper()

    def getException(self, traceID: str) -> dict:
        '''
        return format

            {'trace_id': str, 'error_id': int, 'stack': str, 'time': float}
        '''
        localSession: Session = self.originSession()
        getData: Errors = localSession.query(Errors)\
            .filter(Errors.exception_trace_id == int(traceID, 16)).first()
        if not getData:
            raise BotNotFoundError('无法找到该追踪ID')
        self.originSession.remove()
        return {
            'trace_id': traceID.upper(),
            'error_id': getData.exception_id,
            'stack': getData.exception_stack,
            'time': getData.exception_time
        }

    def writeGroup(self, groupID: int, groupName: str, groupMembers: list):
        localSession: Session = self.originSession()
        queryResult:Groups = localSession.query(Groups)\
            .filter(Groups.group_id == groupID).first()
        if not queryResult:
            enhDict: Groups = EnhancedDict()
            enhDict.group_id = int(groupID)
            enhDict.group_name = str(groupName)
            enhDict.group_member = dumps(groupMembers)
            localSession.add(Groups(**enhDict))
        else:
            queryResult.group_member = dumps(groupMembers)
            queryResult.group_name = str(groupName)
            localSession.add(queryResult)
        localSession.commit()
        self.originSession.remove()

    def getGroup(self, groupID: int) -> dict:
        '''
        return format
        
            {'id': int, 'name': str, 'members': list}
        '''
        localSession: Session = self.originSession()
        getData:Groups = localSession.query(Groups)\
            .filter(Groups.group_id == groupID).first()
        if not getData:
            raise BotNotFoundError('未找到指定群组')
        self.originSession.remove()
        return {
            'id': getData.group_id,
            'name': getData.group_name,
            'members': loads(getData.group_member)
        }

    def writeUser(self,
                  userID: int,
                  username: str,
                  userGroups: list,
                  _inBatch: bool = False):
        localSession: Session = self.originSession()
        queryResult:Users = localSession.query(Users)\
            .filter(Users.user_id == userID).first()
        if not queryResult:
            enhDict: Users = EnhancedDict()
            enhDict.user_id = int(userID)
            enhDict.user_name = str(username)
            enhDict.user_groups = dumps(userGroups)
            commitObj = Users(**enhDict)
        else:
            queryResult.user_name = str(username)
            queryResult.user_groups = dumps(userGroups)
            commitObj = queryResult
        if not _inBatch:
            localSession.add(commitObj)
            localSession.commit()
            self.originSession.remove()
        else:
            self.originSession.remove()
            return commitObj

    def batchWriteUser(self, userList: List[Users]):
        localSession: Session = self.originSession()
        localSession.add_all(userList)
        localSession.commit()
        self.originSession.remove()

    def getUser(self, userID: int) -> dict:
        '''
        return format

            {'id': int, 'name': str, 'groups': list}
        '''
        localSession: Session = self.originSession()
        getData:Users = localSession.query(Users)\
            .filter(Users.user_id == userID).first()
        self.originSession.remove()
        return {
            'id': getData.user_id,
            'name': getData.user_name,
            'groups': dumps(getData.user_groups)
        }

    def writePlugin(self, pluginName: str, status: Dict[str, Dict[str, bool]],
                    setting: Dict[str, Dict[str, Any]]):
        '''
        status format:

            {'group': {str(int): bool}, 'user': {str(int): bool}, 'default': bool}

        setting format:

            {'group': {str(int): Any}, 'user': {str(int): Any}, 'default': Any}
        '''
        localSession: Session = self.originSession()
        queryResult:Plugins = localSession.query(Plugins)\
            .filter(Plugins.plugin_name == pluginName).first()
        if queryResult:
            queryResult.plugin_settings = dumps(setting)
            queryResult.plugin_status = dumps(status)
            localSession.add(queryResult)
        else:
            enhDict: Plugins = EnhancedDict()
            enhDict.plugin_name = str(pluginName)
            enhDict.plugin_status = dumps(status)
            enhDict.plugin_settings = dumps(setting)
            localSession.add(Plugins(**enhDict))
        localSession.commit()
        self.originSession.remove()

    def getPlugin(self, pluginName: str) -> Dict[str, Dict[str, Any]]:
        '''
        return format

            {
                'status': {
                    'group': {str(int): Any},
                    'user': {str(int): Any},
                    'default': Any
                },
                'settings': {
                    'group': {str(int): bool},
                    'user': {str(int): bool},
                    'default': bool
                }
            }
        '''
        localSession: Session = self.originSession()
        queryResult:Plugins=localSession.query(Plugins)\
            .filter(Plugins.plugin_name == pluginName).first()
        if not queryResult:
            raise BotNotFoundError('此插件尚未注册')
        self.originSession.remove()
        return {
            'settings': loads(queryResult.plugin_settings),
            'status': loads(queryResult.plugin_status)
        }

    def listPlugin(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        '''
        return type

            {str: getPlugin(str) ...}
        '''
        localSession: Session = self.originSession()
        queryResult: Iterator[Plugins] = localSession.query(Plugins)
        i: Plugins
        returnList = {
            i.plugin_name: {
                'settings': loads(i.plugin_settings),
                'status': loads(i.plugin_status)
            }
            for i in queryResult
        }
        self.originSession.remove()
        return returnList


database = _database()
