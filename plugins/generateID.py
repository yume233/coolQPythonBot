import json
import random
from datetime import timedelta, datetime
from time import strftime, strptime
from typing import Dict, List, Tuple

from nonebot import CommandSession, on_command

from utils.decorators import SyncToAsync
from utils.message import processSession

__plugin_name__ = 'generateID'

MESSAGE = """
{id_number}
姓名:{name}
性别:{gender}
地址:{address}

生成的数据仅供学习交流使用，并非真实存在的数据！
"""

BIRTH_BEGIN = datetime(1960, 1, 1)
BIRTH_END = datetime(2000, 1, 1)

_AREA_DATA_DIR = './data/data.area.json'
_NAME_DATA_DIR = './data/data.name.json'


def _loadMainData() -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    with open(_AREA_DATA_DIR, 'rt', encoding='utf-8') as f:
        areaLoad = json.load(f)
    with open(_NAME_DATA_DIR, 'rt', encoding='utf-8') as f:
        nameLoad = json.load(f)
    return areaLoad, nameLoad


AREA_DATA, NAME_DATA = _loadMainData()


def _generateIDNumber(areaID: int, gender: int, birth: int) -> str:
    def _checkSum(fullCode: str) -> str:
        assert len(fullCode) == 17
        checkSum = sum([((1 << (17 - i)) % 11) * int(fullCode[i])
                        for i in range(0, 17)])
        checkDigit = (12 - (checkSum % 11)) % 11
        return checkDigit if checkDigit < 10 else 'X'

    orderCode = str(random.randint(10, 99))
    genderCode = str(random.randrange(gender, 10, step=2))
    fullCode = str(areaID) + str(birth) + str(orderCode) + str(genderCode)
    fullCode += str(_checkSum(fullCode))
    return fullCode


@on_command('generate_id_number', aliases=('生成身份证号', '身份证生成'))
@processSession
@SyncToAsync
def _(session: CommandSession):
    areaID = int(random.choice(list(AREA_DATA.keys())))
    areaName = AREA_DATA[str(areaID)]
    randDay = timedelta(
        days=random.randint(0, (BIRTH_END - BIRTH_BEGIN).days) + 1)
    birthDay = strftime("%Y%m%d", (BIRTH_BEGIN + randDay).timetuple())
    gender = random.choice([0, 1])
    randName = random.choice(NAME_DATA[{0: 'female', 1: 'male'}[gender]])
    IDNumber = _generateIDNumber(areaID=areaID, gender=gender, birth=birthDay)
    fullMessage = MESSAGE.format(
        **{
            'id_number': IDNumber,
            'gender': {
                1: '男',
                0: '女'
            }[gender],
            'name': randName,
            'address': areaName
        })
    return fullMessage
