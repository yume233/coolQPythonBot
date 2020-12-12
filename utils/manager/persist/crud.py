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
