from typing import Dict, Iterable, List, Optional, Tuple, Union

from nonebot.matcher import MatcherGroup
from nonebot.rule import Rule
from nonebot.typing import Bot, Event
from pydantic import BaseModel

FeaturesRoot = None


async def privilegeChecker(bot: Bot, event: Event, state: dict) -> bool:
    return True


class FeaturesMatcherGroup(MatcherGroup):
    pass


class FeatureInfo(BaseModel):
    name: str
    description: str = ""
    usage: str = ""


class Feature(BaseModel):
    info: FeatureInfo
    path: Tuple[str, ...]
    parent: "FeaturesView"
    matcher: FeaturesMatcherGroup


ALL_FEATURES: Dict[str, Feature] = {}


class FeaturesView:
    def __init__(self, name: str, parent: Optional["FeaturesView"] = None):
        self._name = name
        self._parent = parent
        self._children: Dict[str, Union["FeaturesView", Feature]] = {}

    @property
    def name(self):
        return self._name

    @property
    def path(self) -> Tuple[str, ...]:
        parentPath: List["FeaturesView"] = []
        parent = self._parent
        while parent is not None:
            parentPath.append(parent)
            parent = parent._parent
        return tuple(*[p.name for p in reversed(parentPath)])

    def new(self, name: str) -> "FeaturesView":
        assert name not in self._children
        child = self.__class__(name=name, parent=self)
        self._children[name] = child
        return child

    def get(self, name: str, info: Optional[FeatureInfo] = None) -> Feature:
        global ALL_FEATURES
        info = info or FeatureInfo(name=name)
        feature = Feature(
            info=info,
            path=(*self.path, info.name),
            parent=self,
            matcher=FeaturesMatcherGroup(rule=Rule(privilegeChecker)),
        )
        ALL_FEATURES[".".join(feature.path)] = self._children[info.name] = feature
        return feature

    def lookup(self, path: Iterable[str]) -> Union["FeaturesView", Feature]:
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
            raise KeyError(f"{childInstance.info.name} is Feature, it has no child!")
        else:
            raise Exception(
                f"Unknown exception occurred during parsing {self=}/{path=}"
            )

    def __getitem__(self, key: str):
        return self._children[key]

    def __iter__(self):
        return self._children.keys()


FeaturesRoot = FeaturesView("HarukaBot")
