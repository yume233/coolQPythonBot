from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String

Base = declarative_base()


class Games(Base):
    __tablename__ = 'games'
    gameid = Column(Integer, primary_key=True)
    name = Column(String)
    gametype = Column(String)
    info = Column(String)
    origin = Column(String)


class database:
    def __init__(self):
        self.engine = create_engine('sqlite:///steamFree.db')
        session = sessionmaker(bind=self.engine)
        self.session = session()

    def addSingle(self, gameid: int, name: str, gametype: str, info: str,
                  origin: str):
        new = Games(
            gameid=gameid,
            name=name,
            gametype=gametype,
            info=info,
            origin=origin)
        self.session.add(new)
        self.session.commit()

    def addMulti(self, argsList):
        multiAddList = [
            Games(
                gameid=gameid,
                name=name,
                gametype=gametype,
                info=info,
                origin=origin)
            for gameid, name, gametype, info, origin in argsList
        ]
        self.session.add_all(multiAddList)
        self.session.commit()