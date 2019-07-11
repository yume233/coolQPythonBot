from nonebot.default_config import *
from datetime import timedelta

API_ROOT = 'http://127.0.0.1:5700'
HOST = '127.0.0.1'
PORT = 8000
SUPERUSERS = {}
COMMAND_START = {'*',',','，'}
NICKNAME = {''}
SESSION_EXPIRE_TIMEOUT = timedelta(seconds=1*60)
SESSION_RUNNING_EXPRESSION = ''
#DEBUG = False