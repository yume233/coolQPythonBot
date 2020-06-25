from base64 import b64encode
from datetime import timedelta
from itertools import count
from time import time
from typing import Iterator, Optional, Union

from nonebot import CommandSession, on_command
from nonebot.message import MessageSegment
from nonebot.permission import GROUP_ADMIN, PRIVATE, SUPERUSER, check_permission

from utils.decorators import SyncToAsync, AsyncToSync
from utils.message import processSession

from . import models, record
from .DAO import MAX_PAGE_SIZE
from .word_cloud import WordcloudGenerator

DatabaseIO = record.DatabaseIO
POWER_GROUP = GROUP_ADMIN | SUPERUSER | PRIVATE
DELTA_TIME = timedelta(days=7)


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


@on_command("wordcloud", aliases=("词云", "高频词"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    latestTime = time() - DELTA_TIME.total_seconds()
    if AsyncToSync(check_permission)(session.bot, session.ctx, GROUP_ADMIN):
        messageIter = messageGenterator(
            group_id=session.ctx["group_id"], latestTime=latestTime
        )
    else:
        messageIter = messageGenterator(
            user_id=session.ctx["user_id"], latestTime=latestTime
        )
    wordcloud = WordcloudGenerator()
    for data in messageIter:
        data: models.RecordsRead
        sentence = data.content
        wordcloud.update(sentence)
    imageData = wordcloud.save()
    return MessageSegment.image(f"base64://{b64encode(imageData).decode()}")
