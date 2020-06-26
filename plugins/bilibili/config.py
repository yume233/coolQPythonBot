import os

from utils.configsReader import configsReader, copyFileInText

CONFIG_PATH = "configs/bilibili.yml"
DEFAULT_PATH = "configs/default.bilibili.yml"

if not os.path.isfile(CONFIG_PATH):
    copyFileInText(DEFAULT_PATH, CONFIG_PATH)

CONFIG = Config = configsReader(CONFIG_PATH, DEFAULT_PATH)
