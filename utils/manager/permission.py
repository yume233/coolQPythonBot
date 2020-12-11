"""
一个权限组可以对应多个成员,这些成员有自己的角色
每个群聊新建一个权限组,为该群聊的每一位成员继承该权限组


每个用户都会继承一个默认权限组
对于群聊:
有"群管理"和"群员"两个权限组,任何群员都应该继承群员权限组
群管理应该继承群管理权限组
对于私聊:
有"临时会话"和"好友"两个权限组,每个私聊都应该继承一个权限组
"""
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from nonebot import permission
from nonebot.message import event_preprocessor
from nonebot.typing import Bot, Event
from pydantic import BaseModel

if TYPE_CHECKING:
    from .manager import Feature, FeaturesBase, FeaturesTree


class PrivilegeRoles(str, Enum):
    SUPERUSER = "superuser"
    GROUP_CHAT = "group"
    GROUP_ADMIN = "group-admin"
    PRIVATE_CHAT = "private-chat"
    FRIEND = "friend"
    TEMPORARY = "temporary"
    DEFAULT = "default"


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

    def get(self, role: PrivilegeRoles, path: str) -> Optional[bool]:
        privilegeData = self.roles.get(role, {})
        return self._verifyPrivilege(path, privilegeData)

    def set(self, role: PrivilegeRoles, path: str, status: Optional[bool] = None):
        privilegeData = self.roles.get(role, {})
        privilegeData.pop(path)
        if status is None:
            return
        privilegeData[path] = status


class UserPrivilege(PrivilegeModel):
    uid: int
    roles: Dict[str, PrivilegeRoles] = {}
    privileges: Dict[str, Dict[str, bool]] = {}


class PrivilegeManager:
    _roleRules = {
        PrivilegeRoles.SUPERUSER: permission.Permission(permission.SUPERUSER),
        PrivilegeRoles.GROUP_ADMIN: (
            permission.Permission(permission.GROUP_ADMIN) or permission.GROUP_OWNER
        ),
        PrivilegeRoles.GROUP_CHAT: permission.Permission(permission.GROUP),
        PrivilegeRoles.PRIVATE_CHAT: permission.Permission(permission.PRIVATE),
        PrivilegeRoles.FRIEND: permission.Permission(permission.PRIVATE_FRIEND),
        PrivilegeRoles.TEMPORARY: (
            permission.Permission(permission.PRIVATE_OTHER) or permission.PRIVATE_GROUP
        ),
    }

    def __init__(self):
        self._privilegeGroups: Dict[str, PrivilegeGroup] = {}
        self._userGroups: Dict[str, Set[str]] = {}

        @event_preprocessor
        async def _(bot: Bot, event: Event, state: dict):
            roles = state["_roles"] = await self.detectRole(bot, event)
            type_ = "group" if PrivilegeRoles.GROUP_CHAT in roles else "private"
            id_ = str(event.group_id if type_ == "group" else event.user_id)
            if (groupName := f"{type_}_{id_}") not in self._privilegeGroups:
                self._privilegeGroups[groupName] = PrivilegeGroup(name=groupName)
            userGroups = self._userGroups.get(str(event.user_id), [])
            userGroups.append()

    async def detectRole(self, bot: Bot, event: Event) -> Set[PrivilegeRoles]:
        return {
            *(
                role
                for role, checker in self._roleRules.items()
                if await checker(bot, event)
            ),
            PrivilegeRoles.DEFAULT,
        }


class PermissionGroups(str, Enum):
    SUPERUSER = "superuser"
    GROUP_ADMIN = "group_admin"
    GROUP_MEMBER = "group_member"
    FRIEND = "friend"
    TEMPORARY = "temporary"
    DEFAULT = "default"


_CHECKERS_RULE = {
    PermissionGroups.SUPERUSER: permission.Permission(permission.SUPERUSER),
    PermissionGroups.GROUP_ADMIN: (
        permission.Permission(permission.GROUP_ADMIN) or permission.GROUP_OWNER
    ),
    PermissionGroups.FRIEND: permission.Permission(permission.PRIVATE_FRIEND),
    PermissionGroups.TEMPORARY: (
        permission.Permission(permission.PRIVATE_OTHER) or permission.PRIVATE_GROUP
    ),
}


async def permissionGroupSelector(bot: Bot, event: Event) -> PermissionGroups:
    for perm, checker in _CHECKERS_RULE.items():
        if await checker(bot=bot, event=event):
            return perm
    return PermissionGroups.DEFAULT
