import sys
from pathlib import Path
from typing import TYPE_CHECKING

from nonebot.log import logger as logger_

from .config import Config

if TYPE_CHECKING:
    from loguru import Logger

LOG_PATH = Path(".") / "data" / "logs"
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_FORMAT = Config["general"]["log"]["format"].as_str().strip()

logger: "Logger" = logger_.opt(colors=True)
logger.remove()
logger.add(sys.stdout, format=LOG_FORMAT, filter=lambda record: record["level"].no < 30)
logger.add(sys.stderr, level="WARNING", format=LOG_FORMAT)
logger.add(str(LOG_PATH / "{time}.log"), encoding="utf-8", enqueue=True)
logger.level(Config["general"]["log"]["level"].as_str().upper())
