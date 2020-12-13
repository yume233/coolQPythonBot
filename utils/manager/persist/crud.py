from typing import Any, Iterable, List, Optional, Tuple

from sqlalchemy import Column
from sqlalchemy.sql.elements import BinaryExpression

from ...exceptions import NotFoundException
from . import models, schema


def _conditionMaker(
    conditions: Iterable[Tuple[Column, Any]]
) -> Optional[BinaryExpression]:
    condition: Optional[BinaryExpression] = None
    for column, value in conditions:
        if value is None:
            continue
        condition = (condition & (column == value)) if condition else (column == value)
    return condition


class Features:
    @staticmethod
    async def create(data: schema.FeatureListCreate):
        feature = await models.FeatureList.create(**data.dict())
        return schema.FeatureListRead.from_orm(feature)

    @staticmethod
    async def read(pid: int):
        feature = await models.FeatureList.get(pid)
        return schema.FeatureListRead.from_orm(feature)

    @staticmethod
    async def delete(pid: int):
        feature = await models.FeatureList.get(pid)
        await feature.delete()


class Privilege:
    @staticmethod
    async def create(data: schema.FeaturePrivilegeCreate):
        privilege = await models.FeaturePrivileges.create(**data.dict())
        return schema.FeaturePrivilegeRead.from_orm(privilege)

    @staticmethod
    async def read(id_: int):
        privilege = await models.FeaturePrivileges.get(id_)
        return schema.FeaturePrivilegeRead.from_orm(privilege)

    @classmethod
    async def readSingle(
        cls,
        group: Optional[int] = None,
        user: Optional[int] = None,
        privilege: Optional[str] = None,
    ):
        results = await cls.readBulk(group, user, privilege)
        if not results:
            raise NotFoundException
        return results[0]

    @staticmethod
    async def readBulk(
        group: Optional[int] = None,
        user: Optional[int] = None,
        privilege: Optional[str] = None,
    ):
        assert (group or user or privilege) is None
        results: List[
            models.FeaturePrivileges
        ] = await models.FeaturePrivileges.query.where(
            _conditionMaker(
                [
                    (models.FeaturePrivileges.group, group),
                    (models.FeaturePrivileges.user, user),
                    (models.FeaturePrivileges.privilege, privilege),
                ]
            )
        ).gino.all()
        return [*map(schema.FeaturePrivilegeRead.from_orm, results)]

    @staticmethod
    async def update(
        id_: int, data: schema.FeaturePrivilegeUpdate
    ) -> schema.FeatureDataRead:
        privilege = await models.FeaturePrivileges.get(id_)
        await privilege.update(**data.dict())
        return schema.FeatureDataRead.from_orm(privilege)

    @staticmethod
    async def delete(id_: int):
        privilege = await models.FeaturePrivileges.get(id_)
        await privilege.delete()


class Data:
    @staticmethod
    async def create(data: schema.FeatureDataCreate):
        privilege = await models.FeatureData.create(**data.dict())
        return schema.FeatureDataRead.from_orm(privilege)

    @staticmethod
    async def read(id_: int):
        privilege = await models.FeatureData.get(id_)
        return schema.FeatureDataRead.from_orm(privilege)

    @classmethod
    async def readSingle(
        cls,
        group: Optional[int] = None,
        user: Optional[int] = None,
        privilege: Optional[str] = None,
    ):
        results = await cls.readBulk(group, user, privilege)
        if not results:
            raise NotFoundException
        return results[0]

    @staticmethod
    async def readBulk(
        group: Optional[int] = None,
        user: Optional[int] = None,
        privilege: Optional[str] = None,
    ):
        assert (group or user or privilege) is None
        results: List[models.FeatureData] = await models.FeatureData.query.where(
            _conditionMaker(
                [
                    (models.FeatureData.group, group),
                    (models.FeatureData.user, user),
                    (models.FeatureData.privilege, privilege),
                ]
            )
        ).gino.all()
        return [*map(schema.FeatureDataRead.from_orm, results)]

    @staticmethod
    async def update(
        id_: int, data: schema.FeatureDataUpdate
    ) -> schema.FeatureDataRead:
        privilege = await models.FeatureData.get(id_)
        await privilege.update(**data.dict())
        return schema.FeatureDataRead.from_orm(privilege)

    @staticmethod
    async def delete(id_: int):
        privilege = await models.FeatureData.get(id_)
        await privilege.delete()
