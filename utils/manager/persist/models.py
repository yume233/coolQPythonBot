from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB

from ...db import db


class FeatureList(db.Model):  # type:ignore
    __tablename__ = "feature_list"
    pid = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.now, nullable=False, index=True)
    name = Column(String(255), index=True, nullable=False, unique=True)
    parent = Column(String(255), index=True)


class FeaturePrivileges(db.Model):  # type:ignore
    __tablename__ = "feature_privileges"
    id = Column(Integer, primary_key=True)
    group = Column(Integer, index=True)
    user = Column(Integer, index=True, nullable=False)
    privilege = Column(
        String(255), ForeignKey(FeatureList.name), index=True, nullable=False
    )
    status = Column(SmallInteger, nullable=False)

    _idx = Index("ix_feature_privileges_unique", group, user, privilege, unique=True)


class FeatureData(db.Model):  # type:ignore
    __tablename__ = "feature_data"
    id = Column(Integer, primary_key=True)
    group = Column(Integer, index=True)
    user = Column(Integer, index=True, nullable=False)
    privilege = Column(
        String(255), ForeignKey(FeatureList.name), index=True, nullable=False
    )
    data = Column(JSONB, nullable=False, default={})

    _idx = Index("ix_feature_data_unique", group, user, privilege, unique=True)
