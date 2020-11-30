from typing import Any, Dict, List, Optional, Tuple

from nonebot.matcher import MatcherGroup
from nonebot.rule import Rule
from nonebot.typing import Bot, Event
from pydantic import BaseModel


class FeatureInfo(BaseModel):
    name: str
    nick: str
    description: str = ""


async def defaultRule(bot: Bot, event: Event, state: dict) -> bool:
    return True


class FeatureImplement:
    def __init__(
        self,
        name: str,
        nick: Optional[str] = None,
        description: str = "",
        usage: str = "",
        parent: Optional["FeatureImplement"] = None,
    ):
        self._parent = parent
        self._name = name
        self._nick = nick or name
        self._description, self.usage = description, usage
        self._children: Dict[str, "FeatureImplement"] = {}
        self._matcherGroup = MatcherGroup(
            rule=Rule(defaultRule), default_state={"_Feature_path": self.path}
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> Optional["FeatureImplement"]:
        return self._parent

    @property
    def path(self) -> Tuple["FeatureImplement", ...]:
        path: List["FeatureImplement"] = []
        parent = self.parent
        while parent is not None:
            path.append(parent)
            parent = parent.parent
        return tuple(reversed(path))

    @property
    def tree(self):
        pass

    @property
    def matchers(self):
        return self._matcherGroup.matchers

    @property
    def newMatcher(self):
        return self._matcherGroup.new

    def getChild(self, name: str) -> "FeatureImplement":
        assert name in self._children
        child = self.__class__(name=name, parent=self)
        self._children[name] = child
        return child


class PluginsRoot:
    _plugins: Dict[str, Any] = {}
    _rootImplement = FeatureImplement("HarukaBot")

    @classmethod
    def new(cls, name: str) -> FeatureImplement:
        assert name in cls._plugins
        newFeature = cls._rootImplement.getChild(name=name)
        cls._plugins[name] = newFeature
        return newFeature

    @classmethod
    def getPluginsTree(cls):
        pass
