import json
from pathlib import Path
from typing import Any, Dict, Literal, Union

import aiofiles

from .models import MsgType

MANAGE_DATA_DIR = Path(".") / "data" / "manager"
MANAGE_DATA_DIR.mkdir(exist_ok=True, parents=True)


PersistDataStruct_T = Dict[
    Literal[MsgType.GROUP, MsgType.PRIVATE],
    Dict[str, Dict[Literal["status", "data"], Dict[str, Union[bool, Dict[str, Any]]]]],
]


class FileOperating:
    _modified: bool = True
    _cache: PersistDataStruct_T = {}

    @classmethod
    async def load(cls, pluginName: str) -> PersistDataStruct_T:
        if not cls._modified:
            return cls._cache
        configDir = MANAGE_DATA_DIR / f"{pluginName}.json"
        if not configDir.exists():
            return {}
        async with aiofiles.open(
            configDir, "rt", encoding="utf-8"
        ) as target:  # type:ignore
            data = json.loads(await target.read())
            assert isinstance(data, dict)
        cls._modified = False
        return data

    @classmethod
    async def save(cls, pluginName: str, data: PersistDataStruct_T) -> int:
        cls._modified = True
        configDir = MANAGE_DATA_DIR / f"{pluginName}.json"
        async with aiofiles.open(
            configDir, "wt", encoding="utf-8"
        ) as target:  # type:ignore
            dumpedData = json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)
            totalWrites = await target.write(dumpedData)
        return totalWrites


class DataPersist:
    pass
