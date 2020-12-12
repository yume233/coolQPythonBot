from typing import Any, Dict, Optional

from pydantic import BaseModel, constr

from ..privilege.models import PrivilegeStatus


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True


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
