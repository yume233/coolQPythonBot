import json
import time

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


class EnhancedDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class subscribeUser(Base):
    __tablename__ = 'subscribe_user'
    subscribe_id = Column(Integer, primary_key=True)
    update_time = Column(Integer, default=0)
    subscribe_people = Column(String, default='[]')
    subscribe_group = Column(String, default='{}')
    origin_data = Column(String)


class subscribeAnime(Base):
    __tablename__ = 'subscribe_anime'
    subscribe_id = Column(Integer, primary_key=True)
    update_time = Column(Integer, default=0)
    subscribe_people = Column(String, default='[]')
    subscribe_group = Column(String, default='{}')
    origin_data = Column(String)


class database:
    def __init__(self):
        self.engine = create_engine('sqlite:///res/bilibiliGuide.db')
        sessionFactory = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        session = scoped_session(sessionFactory)
        self.session = session()
        self.encode = lambda x: json.dumps(x)
        self.decode = lambda x: json.loads(x)

    def addNewSubscriber(self, subscribeID: int, ctx: dict, type: int = 0):
        subscribeClass = subscribeAnime if type else subscribeUser
        databaseGet = self.session.query(subscribeClass).filter_by(
            subscribe_id=subscribeID).all()
        if not databaseGet:
            subscribePeople = []
            subscribeGroup = {}
        else:
            subscribePeople = self.decode(databaseGet[0].subscribe_people)
            subscribeGroup = self.decode(databaseGet[0].subscribe_group)
        if ctx.get('group_id') != None:
            groupID = str(ctx['group_id'])
            subscriber = ctx['user_id']
            if subscribeGroup.get(groupID) != None:
                if not subscriber in subscribeGroup[groupID]:
                    subscribeGroup[groupID].append(subscriber)
            else:
                subscribeGroup[groupID] = [subscriber]
        else:
            subscriber = ctx['user_id']
            subscribePeople.append(subscriber)
        enhDict = EnhancedDict()
        enhDict.subscribe_people = self.encode(subscribePeople)
        enhDict.subscribe_group = self.encode(subscribeGroup)
        #print(databaseGet, subscribeClass, subscribePeople, subscribeGroup)
        if not databaseGet:
            enhDict.subscribe_id = subscribeID
            enhDict.update_time = int(time.time())
            addClass = subscribeClass(**enhDict)
        else:
            addClass = databaseGet[0]
            for perAttr in enhDict:
                setattr(addClass,perAttr,enhDict[perAttr])
        self.session.add(addClass)
        self.session.commit()

    def getSubscriberList(self, subscirbeID: int, type: int = 0) -> dict:
        subscribeClass = subscribeAnime if type else subscribeUser
        databaseGet = self.session.query(subscribeClass).filter_by(
            subscirbe_id=subscirbeID).all()
        if not databaseGet:
            return {}
        subscribePeople = self.decode(databaseGet[0].subscribe_people)
        subscribeGroup = self.decode(databaseGet[0].subscribe_group)
        return {'people': subscribePeople, 'group': subscribeGroup}

    def getSubscribeIDList(self, type: int = 0) -> list:
        subscribeClass = subscribeAnime if type else subscribeUser
        databaseGet = self.session.query(subscribeClass.subscribe_id).all()
        return databaseGet

    def saveOriginData(self, originData: dict, subscribeID: int,
                       type: int = 0):
        updateTime = int(time.time())
        subscribeClass = subscribeAnime if type else subscribeUser
        databaseGet = self.session.query(subscribeClass).filter_by(
            subscribe_id=subscribeID).all()
        if not databaseGet:
            return
        subscribeClass = databaseGet[0]
        subscribeClass.origin_data = self.encode(originData)
        subscribeClass.update_time = updateTime
        self.session.add(subscribeClass)
        self.session.commit()

    def readOriginData(self, subscribeID: int, type: int = 0) -> dict:
        subscribeClass = subscribeAnime if type else subscribeUser
        databaseGet = self.session.query(subscribeClass.origin_data).filter_by(
            subscribe_id=subscribeID).all()
        if not databaseGet:
            return {}
        return self.decode(databaseGet[0])
