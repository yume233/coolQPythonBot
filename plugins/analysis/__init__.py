from base64 import b64encode
from datetime import datetime, timedelta
from itertools import count
from typing import Iterator, Optional

from nonebot import CommandSession, on_command
from nonebot.message import MessageSegment
from nonebot.permission import GROUP_ADMIN, PRIVATE, SUPERUSER

from utils.decorators import SyncToAsync
from utils.message import processSession

from . import models, record
from .access import MAX_PAGE_SIZE
from .chart.cloud import WordcloudGenerator

DatabaseIO = record.DatabaseIO
POWER_GROUP = GROUP_ADMIN | SUPERUSER | PRIVATE
DELTA_TIME = timedelta(days=7)


def messageGenterator(
    group_id: Optional[int] = None,
    user_id: Optional[int] = None,
    latestTime: Optional[datetime] = None,
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
    session.send("开始生成词云")
    latestTime = datetime.now() - DELTA_TIME
    if "group_id" in session.ctx:
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
