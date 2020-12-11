from enum import Enum, IntEnum, auto
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Type, Union

from nonebot import permission
from nonebot.typing import Bot, Event
from pydantic import BaseModel

if TYPE_CHECKING:
    from ..manager import FeaturesTree


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


class DefaultPrivilegeRoles:
    class _BaseRole:
        perm: permission.Permission = permission.Permission(permission.EVERYBODY)

        def __init__(self, root: "FeaturesTree"):
            self._privileges = {
                k: v[self.__class__]
                for k, v in root.allStatus.items()
                if self.__class__ in v
            }

        @classmethod
        async def validator(cls, bot: Bot, event: Event):
            return await cls.perm(bot, event)

        @property
        def privileges(self) -> Dict[str, PrivilegeStatus]:
            return self._privileges

    class Superuser(_BaseRole):
        perm = permission.Permission(permission.SUPERUSER)

    class GroupAdmin(Superuser):
        perm = permission.Permission(permission.GROUP_OWNER) or permission.GROUP_ADMIN

    class GroupChat(GroupAdmin):
        perm = permission.Permission(permission.GROUP)

    class Friend(Superuser):
        perm = permission.Permission(permission.PRIVATE_FRIEND)

    class PrivateChat(Friend):
        perm = permission.Permission(permission.PRIVATE)


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
