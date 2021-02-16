import json
import random
from datetime import datetime, timedelta
from os.path import isfile
from time import strftime
from typing import Dict, List, Tuple
from zipfile import PyZipFile

from nonetrip import CommandSession, on_command
from utils.configsReader import configsReader, copyFileInText
from utils.decorators import SyncToAsync
from utils.message import processSession

__plugin_name__ = "generateID"

_DATA_BINARY_DIR = "./data/id.bin"
_DEFAULT_DIR = "./configs/default.gen_id.yml"
_CONFIG_DIR = "./configs/gen_id.yml"

if not isfile(_CONFIG_DIR):
    copyFileInText(_DEFAULT_DIR, _CONFIG_DIR)
CONFIG = configsReader(_CONFIG_DIR, _DEFAULT_DIR)

MESSAGE = CONFIG.format

BIRTH_BEGIN = datetime(*[int(i) for i in CONFIG.birth.begin])
BIRTH_END = datetime(*[int(i) for i in CONFIG.birth.end])


def _loadMainData() -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    with PyZipFile(_DATA_BINARY_DIR, "r") as zipFile:
        with zipFile.open("name.json", "r") as f:
            nameLoad = json.loads(f.read().decode())
        with zipFile.open("area.json", "r") as f:
            areaLoad = json.loads(f.read().decode())
    return areaLoad, nameLoad


AREA_DATA, NAME_DATA = _loadMainData()


def _generateIDNumber(areaID: int, gender: int, birth: int) -> str:
    def _checkSum(fullCode: str) -> str:
        assert len(fullCode) == 17
        checkSum = sum(
            [((1 << (17 - i)) % 11) * int(fullCode[i]) for i in range(0, 17)]
        )
        checkDigit = (12 - (checkSum % 11)) % 11
        return checkDigit if checkDigit < 10 else "X"

    orderCode = str(random.randint(10, 99))
    genderCode = str(random.randrange(gender, 10, step=2))
    fullCode = str(areaID) + str(birth) + str(orderCode) + str(genderCode)
    fullCode += str(_checkSum(fullCode))
    return fullCode


@on_command("generate_id_number", aliases=("生成身份证号", "身份证生成"))
@processSession
@SyncToAsync
def _(session: CommandSession):
    areaID = int(random.choice(list(AREA_DATA.keys())))
    areaName = AREA_DATA[str(areaID)]
    randDay = timedelta(days=random.randint(0, (BIRTH_END - BIRTH_BEGIN).days) + 1)
    birthDay = strftime("%Y%m%d", (BIRTH_BEGIN + randDay).timetuple())
    gender = random.choice([0, 1])
    randName = random.choice(NAME_DATA[{0: "female", 1: "male"}[gender]])
    IDNumber = _generateIDNumber(areaID=areaID, gender=gender, birth=birthDay)
    fullMessage = MESSAGE.format(
        **{
            "id_number": IDNumber,
            "gender": {1: "男", 0: "女"}[gender],
            "name": randName,
            "address": areaName,
        }
    )
    return fullMessage
