import os
import re
from datetime import timedelta

from nonebot import default_config as dc
from yaml import safe_load, safe_dump

CONFIG_DIR = 'configs/bot.yml'
if os.path.isfile(CONFIG_DIR):
    with open(CONFIG_DIR, 'rt', encoding='utf-8') as f:
        CONFIG_READ: dict = safe_load(f)
        CONFIG_READ = CONFIG_READ if CONFIG_READ else {}
else:
    CONFIG_READ = {}


def timeDeltaRead(key, default: timedelta) -> timedelta:
    configGet = CONFIG_READ.get(key, 0)
    configGet = default if not configGet else timedelta(seconds=configGet)
    return configGet


def getSettings() -> dict:
    from re import compile
    regexp = compile(r'^[0-9A-Z_]+$')
    return {
        k: getattr(settings, k)
        for k in sorted(dir(settings)) if regexp.match(k)
    }


class settings:
    API_ROOT = CONFIG_READ.get('api_root', dc.API_ROOT)
    ACCESS_TOKEN = CONFIG_READ.get('access_token', dc.ACCESS_TOKEN)
    SECRET = CONFIG_READ.get('secret', dc.SECRET)
    HOST = CONFIG_READ.get('host', dc.HOST)
    PORT = CONFIG_READ.get('port', dc.PORT)
    DEBUG = CONFIG_READ.get('debug', dc.DEBUG)

    SUPERUSERS = CONFIG_READ.get('superusers', dc.SUPERUSERS)
    NICKNAME = CONFIG_READ.get('nickname', dc.NICKNAME)

    COMMAND_START = CONFIG_READ.get('command_start', dc.COMMAND_START)
    COMMAND_SEP = CONFIG_READ.get('command_sep', dc.COMMAND_SEP)

    SESSION_EXPIRE_TIMEOUT = timeDeltaRead\
        ('session_expire_timeout',dc.SESSION_EXPIRE_TIMEOUT)
    SESSION_RUN_TIMEOUT = timeDeltaRead\
        ('session_run_timeout',dc.SESSION_RUN_TIMEOUT)
    SESSION_RUNNING_EXPRESSION = CONFIG_READ.get\
        ('session_running_expression',dc.SESSION_RUNNING_EXPRESSION)

    SHORT_MESSAGE_MAX_LENGTH = CONFIG_READ.get\
        ('short_message_max_length',dc.SHORT_MESSAGE_MAX_LENGTH)

    DEFAULT_VALIDATION_FAILURE_EXPRESSION = CONFIG_READ.get\
        ('default_validation_failure_expression',dc.DEFAULT_VALIDATION_FAILURE_EXPRESSION)
    MAX_VALIDATION_FAILURES = CONFIG_READ.get\
        ('max_validation_failure',dc.MAX_VALIDATION_FAILURES)
    TOO_MANY_VALIDATION_FAILURES_EXPRESSION = CONFIG_READ.get\
        ('too_many_validation_failures_expression',dc.TOO_MANY_VALIDATION_FAILURES_EXPRESSION)

    SESSION_CANCEL_EXPRESSION = CONFIG_READ.get\
        ('session_cancel_expression',dc.SESSION_CANCEL_EXPRESSION)

    APSCHEDULER_CONFIG = CONFIG_READ.get\
        ('apscheduler_config',dc.APSCHEDULER_CONFIG)


if not os.path.isfile(CONFIG_DIR):
    with open(CONFIG_DIR, 'wb') as f:
        safe_dump(
            {
                k.lower(): v if type(v) not in {timedelta, set} else
                v.seconds if type(v) != set else list(v)
                for k, v in getSettings().items()
            },
            f,
            encoding='utf-8',
            allow_unicode=True,
            indent=4)
