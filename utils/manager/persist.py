import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple

from loguru import logger
from nonebot.permission import GROUP, Permission
from nonebot.typing import Bot, Event

MANAGE_DATA_DIR = Path(".") / "data" / "manager.json"
MANAGE_DATA_DIR.parent.mkdir(exist_ok=True, parents=True)

_DEFAULT_STRUCT: Dict[str, Dict[str, Dict[str, Any]]] = {"group": {}, "private": {}}


class FileOperating:
    _modified: bool = True
    _cache: Dict[str, Any] = {}

    @classmethod
    def load(cls) -> Dict[str, Any]:
        if not cls._modified:
            return cls._cache
        if not MANAGE_DATA_DIR.exists():
            return _DEFAULT_STRUCT
        with open(MANAGE_DATA_DIR, "rt", encoding="utf-8") as target:
            data = json.load(target)
            assert isinstance(data, dict)
        cls._modified, cls._cache = False, data
        return data

    @classmethod
    def save(cls, data: Dict[str, Any]) -> int:
        cls._modified = True
        with open(MANAGE_DATA_DIR, "wt", encoding="utf-8") as target:
            dumpedData = json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)
            totalWrites = target.write(dumpedData)
        logger.debug(
            "Persistence of manage data finished, "
            f"file size:<b>{totalWrites}bytes</b>"
        )
        return totalWrites


class ManageData:
    _checkGroup = Permission(GROUP)

    def __init__(
        self, type_: Literal["group", "private"], id_: int, path: Tuple[str, ...]
    ):
        self._type, self._id, self._path = type_, id_, path

    @classmethod
    async def new(cls, bot: Bot, event: Event, state: dict):
        type_ = "group" if await cls._checkGroup(bot, event) else "private"
        id_ = event.group_id if type_ == "group" else event.user_id
        return cls(type_, id_, state["_feature_path"])  # type:ignore

    @property
    def _properties(self) -> Dict[str, Dict[str, Any]]:
        data = FileOperating.load()
        return deepcopy(data[self._type].get(str(self._id), {"status": {}, "data": {}}))

    @_properties.setter
    def _properties(self, value: Dict[str, Dict[str, Any]]):
        data = FileOperating.load()
        data[self._type][str(self._id)] = value
        FileOperating.save(data)

    @property
    def status(self) -> Optional[bool]:
        statusMap: Dict[str, bool] = self._properties["status"]
        if (stringPath := ".".join(self._path)) in statusMap:
            return statusMap[stringPath]
        for parent in map(
            lambda i: ".".join(self._path[:-i]), range(1, len(self._path))
        ):
            if parent not in statusMap:
                continue
            return statusMap[parent]
        return None

    @status.setter
    def status(self, value: Optional[bool]):
        data = self._properties
        path = ".".join(self._path)
        if value is None:
            data["status"].pop(path)
        else:
            data["status"][".".join(self._path)] = value
        self._properties = data

    @property
    def data(self) -> Optional[Dict[str, Any]]:
        return deepcopy(self._properties["data"].get(".".join(self._path)))

    @data.setter
    def data(self, value: Dict[str, Any]):
        data = self._properties
        data["data"][".".join(self._path)] = value
        self._properties = data
