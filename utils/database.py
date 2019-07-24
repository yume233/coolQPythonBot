from secrets import token_hex

from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from .customConfig import configs
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
        self.engine = create_engine(configs.database.address)
        Base.metadata.create_all(self.engine)
        self.sessionFactory = sessionmaker(bind=self.engine)
        self.originSession = scoped_session(self.sessionFactory)

    def catchException(self, time: float, stack: str) -> str:
        localSession: Session = self.originSession()
        traceID = token_hex(8)
        enhDict: Errors = EnhancedDict()
        enhDict.exception_trace_id = int(traceID, 16)
        enhDict.exception_time = float(time)
        enhDict.exception_stack = stack
        localSession.add(Errors(**enhDict))
        localSession.commit()
        self.originSession.remove()
        return traceID.upper()

    def getException(self, traceID: str) -> dict:
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
