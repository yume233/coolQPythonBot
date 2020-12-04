from pathlib import Path

from loguru import Logger
from nonebot.log import logger as logger_

from .config import Config

LOG_PATH = Path(".") / "data" / "logs"
LOG_PATH.mkdir(parents=True, exist_ok=True)

logger: Logger = logger_.opt(colors=True)
logger.add(str(LOG_PATH / "{time}.log"), encoding="utf-8", enqueue=True)
logger.level(Config["general"]["log"]["level"].as_str().upper())  # type:ignore
