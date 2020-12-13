from typing import TYPE_CHECKING

from gino.ext.starlette import Gino  # type:ignore
from sqlalchemy.engine.url import URL

from .config import Config

if TYPE_CHECKING:
    from gino_starlette import Gino  # noqa:F811

DBConfig = Config["database"]

DB_DSN = URL(
    drivername="postgresql",
    host=DBConfig["connection"]["host"].as_str(),
    port=DBConfig["connection"]["port"].as_number(),
    username=DBConfig["connection"]["user"].as_str(),
    password=DBConfig["connection"]["password"].as_str(),
    database=DBConfig["connection"]["database"].as_str(),
)

db = Gino(
    dsn=str(DB_DSN),
    pool_min_size=DBConfig["pool"]["min"].as_number(),
    pool_max_size=DBConfig["pool"]["max"].as_number(),
    echo=DBConfig["echo"].as_bool(),
    retry_limit=DBConfig["retry"]["limit"].as_number(),
    retry_interval=DBConfig["retry"]["interval"].as_number(),
)
