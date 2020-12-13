from sqlalchemy import JSON, Column, ForeignKey, Index, Integer, SmallInteger, String

from ...db import db


class AllPrivileges(db.Model):  # type:ignore
    __tablename__ = "feature_privilege"
    pid = Column(Integer, primary_key=True)
    name = Column(String(255), index=True, nullable=False, unique=True)
    parent = Column(String(255), index=True)


class FeaturePrivileges(db.Model):  # type:ignore
    __tablename__ = "feature_statuses"
    id = Column(Integer, primary_key=True)
    group = Column(Integer, index=True)
    user = Column(Integer, index=True, nullable=False)
    privilege = Column(
        String(255), ForeignKey(AllPrivileges.name), index=True, nullable=False
    )
    status = Column(SmallInteger, nullable=False)

    _idx = Index("ix_feature_privileges_unique", group, user, privilege, unique=True)


class FeatureData(db.Model):  # type:ignore
    __tablename__ = "feature_data"
    id = Column(Integer, primary_key=True)
    group = Column(Integer, index=True)
    user = Column(Integer, index=True, nullable=False)
    privilege = Column(
        String(255), ForeignKey(AllPrivileges.name), index=True, nullable=False
    )
    data = Column(JSON, nullable=False, default="{}")

    _idx = Index("ix_feature_data_unique", group, user, privilege, unique=True)
