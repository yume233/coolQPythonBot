from enum import IntEnum, auto

from nonebot import permission
from nonebot.typing import Bot, Event


class PermissionGroups(IntEnum):
    SUPERUSER = auto()
    GROUP_ADMIN = auto()
    GROUP_MEMBER = auto()
    FRIEND = auto()
    TEMPORARY = auto()
    DEFAULT = auto()


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
