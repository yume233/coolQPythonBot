from typing import Any, Dict, List, Optional, Union

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import Session, sessionmaker
from utils.botConfig import settings
from utils.exception import BotExistError, BotNotFoundError

from . import models, tables
from .config import Config

DATABASE_URL: str = Config.db.uri
DATABASE_CONFIG: Dict[str, Any] = {**Config.db.settings}
DATABASE_DEBUG: bool = Config.db.echo
MAX_PAGE_SIZE = 200


class DatabaseTransaction:
    def __init__(self, session: Session):
        self._session = session

    def __enter__(self) -> Session:
        self._session.begin(subtransactions=True)
        return self._session

    def __exit__(self, *args):
        if self._session.transaction is None:
            return
        self._session.transaction.__exit__(*args)


class RecordDAO:
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL, connect_args=DATABASE_CONFIG or None, echo=DATABASE_DEBUG
        )
        tables.Base.metadata.create_all(bind=self.engine)
        self.sessionFactory = sessionmaker(
            bind=self.engine, autocommit=True, autoflush=True
        )

    @staticmethod
    def table2dict(table: Any) -> Dict[str, Any]:
        return dict(table.__dict__)

    def connect(self) -> DatabaseTransaction:
        return DatabaseTransaction(self.sessionFactory())

    def recordCreate(self, data: models.RecordsCreate) -> models.RecordsRead:
        with self.connect() as session:
            table = tables.ChatRecords(**dict(data))
            session.add(table)
            session.flush()
            result = models.RecordsRead(**self.table2dict(table))
        return result

    def recordRead(self, rid: int) -> models.RecordsRead:
        with self.connect() as session:
            result = (
                session.query(tables.ChatRecords)
                .filter(tables.ChatRecords.rid == rid)
                .first()
            )
            if not result:
                raise BotNotFoundError("在数据库中没有相应记录")
            data = models.RecordsRead(**self.table2dict(result))
        return data

    def recordReadBulk(
        self,
        user: Optional[int] = None,
        group: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        reversed: bool = False,
    ) -> List[models.RecordsRead]:
        with self.connect() as session:
            result = (
                session.query(tables.ChatRecords)
                .filter(
                    (tables.ChatRecords.sender == user) if user is not None else True
                )
                .filter(
                    (tables.ChatRecords.group == group) if group is not None else True
                )
                .order_by(
                    desc(tables.ChatRecords.time)
                    if reversed
                    else tables.ChatRecords.time
                )
                .limit(limit if limit <= MAX_PAGE_SIZE else MAX_PAGE_SIZE)
                .offset(offset)
            )
            allData = [models.RecordsRead(**self.table2dict(i)) for i in result]
        return allData

    def recordDelete(self, rid: int):
        with self.connect() as session:
            result = (
                session.query(tables.ChatRecords)
                .filter(tables.ChatRecords.rid == rid)
                .first()
            )
            if not result:
                raise BotNotFoundError("在数据库中没有相应记录")
            session.delete(result)
        return

    def userCreate(
        self,
        data: models.Users,
        raiseException: bool = True,
        updateIfExist: bool = False,
    ) -> Optional[models.Users]:
        with self.connect() as session:
            if session.query(tables.Users).filter(tables.Users.uid == data.uid).first():
                if updateIfExist:
                    return self.userUpdate(data)
                elif raiseException:
                    raise BotExistError("此条记录已在数据库中存在")
                else:
                    return
            table = tables.Users(**dict(data))
            session.add(table)
            session.flush()
            result = models.Users(**self.table2dict(table))
        return result

    def userRead(
        self, uid: Optional[int] = None, offset: int = 0, limit: int = 100
    ) -> Union[List[models.Users], models.Users]:
        with self.connect() as session:
            result = (
                session.query(tables.Users)
                .filter((tables.Users.uid == uid) if uid is not None else True)
                .order_by(tables.Users.uid)
                .limit(limit if limit <= MAX_PAGE_SIZE else MAX_PAGE_SIZE)
                .offset(offset)
                .all()
            )
            if (uid is not None) and (not result):
                raise BotNotFoundError("在数据库中没有相应记录")
            dataList = [models.Users(**self.table2dict(i)) for i in result]
        return dataList if uid is None else dataList[0]

    def userUpdate(self, data: models.Users) -> models.Users:
        with self.connect() as session:
            result = (
                session.query(tables.Users).filter(tables.Users.uid == data.uid).first()
            )
            if not result:
                raise BotNotFoundError("在数据库中没有相应记录")
            for k, v in data.dict().items():
                if getattr(result, k) == v:
                    continue
                setattr(result, k, v)
            session.flush()
            data = models.Users(**self.table2dict(result))
        return data

    def userDelete(self, uid: int):
        with self.connect() as session:
            result = session.query(tables.Users).filter(tables.Users.uid == uid).first()
            if not result:
                raise BotNotFoundError("在数据库中没有相应记录")
            session.delete(result)
        return

    def groupCreate(
        self,
        data: models.Groups,
        raiseException: bool = True,
        updateIfExist: bool = False,
    ) -> Optional[models.Groups]:
        with self.connect() as session:
            if (
                session.query(tables.Groups)
                .filter(tables.Groups.gid == data.gid)
                .first()
            ):
                if updateIfExist:
                    return self.groupUpdate(data)
                elif raiseException:
                    raise BotExistError("此条记录已在数据库中存在")
                else:
                    return
            table = tables.Groups(**dict(data))
            session.add(table)
            session.flush()
            result = models.Groups(**self.table2dict(table))
        return result

    def groupRead(
        self, gid: Optional[int] = None, offset: int = 0, limit: int = 100
    ) -> Union[List[models.Groups], models.Groups]:
        with self.connect() as session:
            result = (
                session.query(tables.Groups)
                .filter((tables.Groups.gid == gid) if gid is not None else True)
                .order_by(tables.Groups.uid)
                .limit(limit if limit <= MAX_PAGE_SIZE else MAX_PAGE_SIZE)
                .offset(offset)
                .all()
            )
            if (gid is not None) and (not result):
                raise BotNotFoundError("在数据库中没有相应记录")
            dataList = [models.Groups(**self.table2dict(i)) for i in result]
        return dataList if gid is None else dataList[0]

    def groupUpdate(self, data: models.Groups) -> models.Groups:
        with self.connect() as session:
            result = (
                session.query(tables.Groups)
                .filter(tables.Groups.gid == data.gid)
                .first()
            )
            if not result:
                raise BotNotFoundError("在数据库中没有相应记录")
            for k, v in data.dict().items():
                if getattr(result, k) == v:
                    continue
                setattr(result, k, v)
            session.flush()
            data = models.Groups(**self.table2dict(result))
        return data

    def groupDelete(self, gid: int):
        with self.connect() as session:
            result = (
                session.query(tables.Groups).filter(tables.Groups.gid == gid).first()
            )
            if not result:
                raise BotNotFoundError("在数据库中没有相应记录")
            session.delete(result)
        return
