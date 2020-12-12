from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.plugin import MatcherGroup
from nonebot.rule import Rule
from nonebot.typing import Bot, Event

from ..log import logger
from .privilege import PrivilegeGroup, PrivilegeManager, PrivilegeRoles


class FeaturesMatcherGroup(MatcherGroup):
    pass


class FeaturesBase:
    def __init__(
        self,
        name: str,
        description: str = "",
        usage: str = "",
        parent: Optional["FeaturesBase"] = None,
        status: Optional[Dict[PrivilegeRoles, bool]] = None,
        data: Optional[Dict[PrivilegeRoles, Dict[str, Any]]] = None,
    ):
        self._name, self.description, self.usage = name, description, usage
        self._parent, self._status, self._data = parent, status, data

        @event_preprocessor
        async def _appendManageData(bot: Bot, event: Event, state: dict):
            if event.type == "meta_event" and event.detail_type == "heartbeat":
                raise IgnoredException(f"Ignored meta event: {event.__dict__}.")
            state["_feature_path"] = self.path
            state["_feature_data"] = await ManageData.new(bot, event, state)

        logger.trace(f"Feature <e>{self.path}</e> initiated")

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def path(self) -> Tuple[str, ...]:
        parentPath: List[str] = []
        parent = self
        while parent is not None:
            parentPath.append(parent.name)
            parent = parent.parent
        return tuple(reversed(parentPath))

    @property
    def strPath(self) -> str:
        return ".".join(self.path)

    @property
    def defaultStatus(self) -> Dict[PrivilegeRoles, bool]:
        return self._status or self.parent.defaultStatus

    async def isEnabled(self, bot: Bot, event: Event, state: dict) -> bool:
        data: ManageData = state["_feature_data"]
        if data.status is not None:
            return data.status
        group = await PrivilegeRoleselector(bot, event)
        return self.defaultStatus[
            group if group in self.defaultStatus else PrivilegeRoles.DEFAULT
        ]


class Feature(FeaturesBase):
    @property
    def matcher(self):
        if hasattr(self, "_matcher"):
            return self._matcher
        self._matcher = FeaturesMatcherGroup(rule=Rule(self.isEnabled))
        return self._matcher


class FeaturesTree(FeaturesBase):
    def __init__(
        self,
        name: str,
        description: str = "",
        usage: str = "",
        parent: Optional["FeaturesBase"] = None,
        status: Optional[Dict[PrivilegeRoles, bool]] = None,
        data: Optional[Dict[PrivilegeRoles, Dict[str, Any]]] = None,
    ):
        super().__init__(
            name,
            description=description,
            usage=usage,
            parent=parent,
            status=status,
            data=data,
        )
        self._children: Dict[str, FeaturesBase] = {}

    @property
    def allStatus(self) -> Dict[str, Dict[PrivilegeRoles, bool]]:
        statuses = {self.strPath: self.defaultStatus}
        for child in self._children.values():
            statuses[child.strPath] = child.defaultStatus
            if isinstance(child, self.__class__):
                statuses.update(child.allStatus)
        return statuses

    def inherit(
        self,
        name: str,
        description: str = "",
        usage: str = "",
        status: Optional[Dict[PrivilegeRoles, bool]] = None,
        data: Optional[Dict[PrivilegeRoles, Dict[str, Any]]] = None,
    ):
        self[name] = child = self.__class__(
            name,
            description=description,
            usage=usage,
            parent=self,
            status=status,
            data=data,
        )
        return child

    __call__ = inherit

    def lookup(self, path: Iterable[str]) -> Union["FeaturesBase", Feature]:
        root, *children = path
        assert root == self.name
        if not children:
            return self
        child, *grandchildren = children
        childInstance = self._children[child]
        if not grandchildren:
            return childInstance
        elif isinstance(childInstance, self.__class__):
            return childInstance.lookup(children)
        elif isinstance(childInstance, Feature):
            raise KeyError(f"{childInstance.name} is Feature, it has no child!")
        else:
            raise Exception(f"Unknown exception occurred during parsing {self}/{path}")

    def feature(
        self,
        name: str,
        description: str = "",
        usage: str = "",
        status: Optional[Dict[PrivilegeRoles, bool]] = None,
        data: Optional[Dict[PrivilegeRoles, Dict[str, Any]]] = None,
    ) -> Feature:
        return Feature(
            name,
            description=description,
            usage=usage,
            parent=self,
            status=status,
            data=data,
        )

    def __getitem__(self, key: str):
        return self._children[key]

    def __setitem__(self, key: str, value: Any):
        if key in self._children:
            raise KeyError(f"Key {key} already exists at {self.name}.")
        if not key.isalnum():
            raise KeyError(f"Key {key} must be a number or alpha.")
        self._children[key] = value

    def __iter__(self):
        return self._children.keys()


FeaturesRoot = FeaturesTree("IzumiBot", status={PrivilegeRoles.SUPERUSER: True})
