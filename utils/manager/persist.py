import json
from pathlib import Path
from typing import Any, Dict

import aiofiles

MANAGE_DATA_DIR = Path(".") / "data" / "manager"
MANAGE_DATA_DIR.mkdir(exist_ok=True, parents=True)


class FileOperating:
    @staticmethod
    async def load(pluginName: str) -> Dict[str, Any]:
        configDir = MANAGE_DATA_DIR / f"{pluginName}.json"
        if not configDir.exists():
            return {}
        async with aiofiles.open(
            configDir, "rt", encoding="utf-8"
        ) as target:  # type:ignore
            data = json.loads(await target.read())
            assert isinstance(data, dict)
        return data

    @staticmethod
    async def save(pluginName: str, data: Dict[str, Any]) -> int:
        configDir = MANAGE_DATA_DIR / f"{pluginName}.json"
        async with aiofiles.open(
            configDir, "wt", encoding="utf-8"
        ) as target:  # type:ignore
            dumpedData = json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)
            totalWrites = await target.write(dumpedData)
        return totalWrites
