import os

from utils.configsReader import configsReader, copyFileInText

CONFIG_PATH = 'configs/Image2Anime.yml'
DEFAULT_PATH = 'configs/default.Image2Anime.yml'

if not os.path.isfile(CONFIG_PATH):
    copyFileInText(DEFAULT_PATH, CONFIG_PATH)

CONFIG = Config = configsReader(CONFIG_PATH, DEFAULT_PATH)