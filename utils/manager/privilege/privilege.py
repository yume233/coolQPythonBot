from typing import TYPE_CHECKING, Dict

from nonebot import permission
from nonebot.message import event_preprocessor
from nonebot.typing import Bot, Event

from .models import PrivilegeGroup, PrivilegeRoles, UserPrivilege

if TYPE_CHECKING:
    from ..manager import FeaturesRoot


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
        self._groups: Dict[str, PrivilegeGroup] = {}
        self._users: Dict[str, UserPrivilege] = {}

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
