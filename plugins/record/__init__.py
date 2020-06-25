from itertools import count
from typing import Iterator, Optional, Union

from nonebot import CommandSession, on_command
from nonebot.message import MessageSegment
from nonebot.permission import GROUP_ADMIN, PRIVATE, SUPERUSER

from utils.decorators import SyncToAsync
from utils.message import processSession

from . import models, record
from .DAO import MAX_PAGE_SIZE
from .word_cloud import WordcloudGenerator

DatabaseIO = record.DatabaseIO
POWER_GROUP = GROUP_ADMIN | SUPERUSER | PRIVATE

def messageGenterator(
    group_id: Optional[int] = None,
    user_id: Optional[int] = None,
    latestTime: Optional[Union[float, int]] = None,
) -> Iterator[models.RecordsRead]:
    for offset in count(0, MAX_PAGE_SIZE):
        result = DatabaseIO.recordReadBulk(
            user=user_id,
            group=group_id,
            reversed=True,
            limit=MAX_PAGE_SIZE,
            offset=offset,
        )
        if not result:
            break
        for data in result:
            if latestTime is not None:
                if data.time <= latestTime:
                    break
            yield data
    return
