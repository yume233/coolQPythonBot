from enum import IntEnum, auto
from typing import Dict, Optional

from pydantic import BaseModel


class PrivilegeRoles(IntEnum):
    SUPERUSER = auto()
    GROUP_ADMIN = auto()
    FRIEND = auto()
    GROUP_CHAT = auto()
    TEMPORARY = auto()
    PRIVATE_CHAT = auto()
    DEFAULT = auto()


class PrivilegeModel(BaseModel):
    @staticmethod
    def _verifyPrivilege(path: str, privMap: Dict[str, bool]) -> Optional[bool]:
        for depth in range(len(path.split("."))):
            if (parent := path.rsplit(".", depth)[0]) in privMap:
                return privMap[parent]
        return None


class PrivilegeGroup(PrivilegeModel):
    name: str
    roles: Dict[PrivilegeRoles, Dict[str, bool]] = {}
    parent: Optional["PrivilegeGroup"] = None

    def get(self, role: PrivilegeRoles, path: str) -> Optional[bool]:
        privilegeData = self.roles.get(role, {})
        if (status := self._verifyPrivilege(path, privilegeData)) is not None:
            return status
        elif self.parent is not None:
            return self.parent.get(role, path)
        return None

    def set(self, role: PrivilegeRoles, path: str, status: Optional[bool] = None):
        privilegeData = self.roles.get(role, {})
        privilegeData.pop(path)
        if status is None:
            return
        privilegeData[path] = status


class UserPrivilege(PrivilegeModel):
    uid: int
    groups: Dict[str, PrivilegeGroup] = {}
    roles: Dict[PrivilegeRoles, Dict[str, bool]] = {}

    def get(self, id_: str, role: PrivilegeRoles, path: str) -> Optional[bool]:
        data = self.roles.get(role, {})
        if (userPriv := self._verifyPrivilege(path, data)) is not None:
            return userPriv
        return self.groups[id_].get(role, path)

    def set(self, role: PrivilegeRoles, path: str, status: Optional[bool] = None):
        privilegeData = self.roles.get(role, {})
        privilegeData.pop(path)
        if status is None:
            return
        privilegeData[path] = status
