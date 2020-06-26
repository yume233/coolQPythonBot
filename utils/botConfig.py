import os
from datetime import timedelta

from nonebot import default_config as dc
from yaml import safe_load

CONFIG_DIR = "./configs/bot.yml"
DEFAULT_CONFIG_DIR = "./configs/default.bot.yml"


def initConfig() -> dict:
    """Initialize configuration variables

    Returns
    -------
    dict
        [description]
    """
    if not os.path.isfile(CONFIG_DIR):
        with open(CONFIG_DIR, "wb") as _:
            pass
    with open(CONFIG_DIR, "rt+", encoding="utf-8") as config, open(
        DEFAULT_CONFIG_DIR, "rt", encoding="utf-8"
    ) as default:
        defaultReadText = default.read()
        configRead: dict = safe_load(config)
        defaultRead: dict = safe_load(defaultReadText)
        if not configRead:
            config.write(defaultReadText)
            configRead = defaultRead
    return configRead


CONFIG_READ = initConfig()


def readSecondsAsTimeDelta(key: str, default: timedelta) -> timedelta:
    """Read the seconds in the configuration file as a `timedelta` object

    Parameters
    ----------
    key : str
        Key names in the configuration file
    default : timedelta
        If not found, the default value

    Returns
    -------
    timedelta
        [description]
    """
    configGet: int = CONFIG_READ.get(key, 0)
    return timedelta(seconds=configGet) if configGet else default


def convertSettingsToDict() -> dict:
    """Converting the `settings` object to a `dict`

    Returns
    -------
    dict
        [description]
    """
    return {
        k: getattr(settings, k)
        for k in sorted(
            filter(lambda x: x.isupper() and not x.startswith("_"), dir(settings))
        )
    }


class settings:
    API_ROOT = None
    ACCESS_TOKEN = CONFIG_READ.get("access_token", dc.ACCESS_TOKEN)
    SECRET = CONFIG_READ.get("secret", dc.SECRET)
    HOST = CONFIG_READ.get("host", dc.HOST)
    PORT = CONFIG_READ.get("port", dc.PORT)
    DEBUG = CONFIG_READ.get("debug", dc.DEBUG)

    SUPERUSERS = CONFIG_READ.get("superusers", dc.SUPERUSERS)
    NICKNAME = CONFIG_READ.get("nickname", dc.NICKNAME)

    COMMAND_START = CONFIG_READ.get("command_start", dc.COMMAND_START)
    COMMAND_SEP = CONFIG_READ.get("command_sep", dc.COMMAND_SEP)

    SESSION_EXPIRE_TIMEOUT = readSecondsAsTimeDelta(
        "session_expire_timeout", dc.SESSION_EXPIRE_TIMEOUT
    )
    SESSION_RUN_TIMEOUT = readSecondsAsTimeDelta(
        "session_run_timeout", dc.SESSION_RUN_TIMEOUT
    )
    SESSION_RUNNING_EXPRESSION = CONFIG_READ.get(
        "session_running_expression", dc.SESSION_RUNNING_EXPRESSION
    )

    SHORT_MESSAGE_MAX_LENGTH = CONFIG_READ.get(
        "short_message_max_length", dc.SHORT_MESSAGE_MAX_LENGTH
    )

    DEFAULT_VALIDATION_FAILURE_EXPRESSION = CONFIG_READ.get(
        "default_validation_failure_expression",
        dc.DEFAULT_VALIDATION_FAILURE_EXPRESSION,
    )
    MAX_VALIDATION_FAILURES = CONFIG_READ.get(
        "max_validation_failure", dc.MAX_VALIDATION_FAILURES
    )
    TOO_MANY_VALIDATION_FAILURES_EXPRESSION = CONFIG_READ.get(
        "too_many_validation_failures_expression",
        dc.TOO_MANY_VALIDATION_FAILURES_EXPRESSION,
    )

    SESSION_CANCEL_EXPRESSION = CONFIG_READ.get(
        "session_cancel_expression", dc.SESSION_CANCEL_EXPRESSION
    )

    APSCHEDULER_CONFIG = CONFIG_READ.get("apscheduler_config", dc.APSCHEDULER_CONFIG)

    DATABASE_ADDRESS = CONFIG_READ.get("database_address", "sqlite:///database.sqlite")
    DATABASE_DEBUG = CONFIG_READ.get("database_debug", False)

    THREAD_POOL_NUM = CONFIG_READ.get("thread_pool_num", 16)
