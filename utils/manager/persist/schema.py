from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, constr


class PrivilegeStatus(IntEnum):
    """
    - PROHIBITED: Prohibit anyone to change this
    - DISABLED: Disabled usage by default
    - ENABLED: Enabled usage by default
    - FORCED: Force this function open which is cannot be changed
    """

    PROHIBITED = -1
    DISABLED = 0
    ENABLED = 1
    FORCED = 2


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True


class BaseFeatureList(BaseSchema):
    name: constr(max_length=255)  # type:ignore
    parent: constr(max_length=255)  # type:ignore


class FeatureListCreate(BaseFeatureList):
    pass


class FeatureListRead(BaseFeatureList):
    pid: int
    time: datetime


class BaseFeaturePrivilege(BaseSchema):
    group: Optional[int]
    user: int
    privilege: constr(max_length=255)  # type:ignore
    status: PrivilegeStatus


class FeaturePrivilegeCreate(BaseFeaturePrivilege):
    pass


class FeaturePrivilegeUpdate(BaseFeaturePrivilege):
    pass


class FeaturePrivilegeRead(BaseFeaturePrivilege):
    id: int


class BaseFeatureData(BaseSchema):
    group: Optional[int]
    user: int
    privilege: constr(max_length=255)  # type:ignore
    data: Dict[str, Any]


class FeatureDataCreate(BaseFeaturePrivilege):
    pass


class FeatureDataUpdate(BaseFeaturePrivilege):
    pass


class FeatureDataRead(BaseFeaturePrivilege):
    id: int
