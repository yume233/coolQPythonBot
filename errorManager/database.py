from binascii import crc32
from json import dumps
from time import time
from traceback import format_stack

from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


class EnhancedDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class exceptions(Base):
    __tablename__ = 'exceptions'
    eid = Column(Integer, primary_key=True)
    etime = Column(Float, index=True)
    einfo = Column(String)
    estack = Column(String)


class database:
    def __init__(self):
        engine = create_engine('sqlite:///res/exception.db')
        Base.metadata.create_all(engine)
        sessionFactory = sessionmaker(bind=engine)
        self.origin_session = scoped_session(sessionFactory)
        self.session = self.origin_session()

    def catchExcept(self, errmsg: str) -> str:
        enhDict = EnhancedDict()
        enhDict.estack = dumps(format_stack())
        enhDict.einfo = str(errmsg)
        enhDict.etime = time()
        enhDict.eid = crc32(str(enhDict.etime))
        formatEid = hex(enhDict.eid).replace('0x').upper()
        self.session.add(exceptions(**enhDict))
        self.session.commit()
        return formatEid
    
    def getExcept(self,errID:str)->dict:
        trueID = int(errID,16)
        baseGet =self.session.query(exceptions).filter_by(eid=trueID).all()
        if not baseGet:
            return 
        getResult:exceptions = baseGet[0]
        returnData = {
            'stack':getResult.estack,
            'time':getResult.etime,
            'info':getResult.einfo
        }
        return returnData
