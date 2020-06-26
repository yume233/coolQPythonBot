import json
from time import time

from sqlalchemy import Column, Float, ForeignKey, Integer, String, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JsonIO(TypeDecorator):
    impl = String

    def process_bind_param(self, value: dict, dialect):
        return json.dumps(value)

    def process_result_value(self, value: str, dialect):
        return json.loads(value)


class Users(Base):
    __tablename__ = "users"
    uid = Column(Integer, primary_key=True)
    nickname = Column(String, index=True, nullable=False)
    data = Column(JsonIO, nullable=False)


class Groups(Base):
    __tablename__ = "groups"
    gid = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False)
    members = Column(JsonIO, nullable=False)


class ChatRecords(Base):
    __tablename__ = "records"
    rid = Column(Integer, primary_key=True)
    sender = Column(Integer, ForeignKey("users.uid"), index=True, nullable=False)
    group = Column(Integer, ForeignKey("groups.gid"), index=True)
    time = Column(Float, index=True, nullable=False, default=time)
    content = Column(String, nullable=False)
    ctx = Column(JsonIO, nullable=False)
