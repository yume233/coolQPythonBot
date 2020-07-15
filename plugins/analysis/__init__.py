from base64 import b64encode
import datetime
from itertools import count
from typing import Iterator, Optional

from nonebot import CommandSession, on_command
from nonebot.message import MessageSegment
from nonebot.permission import GROUP_ADMIN, PRIVATE, SUPERUSER

from utils.decorators import SyncToAsync
from utils.message import processSession

from . import models, record
from .access import MAX_PAGE_SIZE
from .chart.cloud import WordcloudMaker
from .chart.statistics import DataFrameMaker, Chart

DatabaseIO = record.DatabaseIO
POWER_GROUP = GROUP_ADMIN | SUPERUSER | PRIVATE
DELTA_TIME = datetime.timedelta(days=7)


def messageGenterator(
    group_id: Optional[int] = None,
    user_id: Optional[int] = None,
    latestTime: Optional[datetime.datetime] = None,
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


def _time2Int(time: datetime.time) -> int:
    return datetime.timedelta(
        hours=time.hour,
        minutes=time.minute,
        seconds=time.second,
        microseconds=time.microsecond,
    ).total_seconds()


@on_command("wordcloud", aliases=("词云", "高频词"), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    session.send("开始生成词云")
    latestTime = datetime.datetime.now() - DELTA_TIME
    if "group_id" in session.ctx:
        messageIter = messageGenterator(
            group_id=session.ctx["group_id"], latestTime=latestTime
        )
    else:
        messageIter = messageGenterator(
            user_id=session.ctx["user_id"], latestTime=latestTime
        )
    wordcloud = WordcloudMaker()
    for data in messageIter:
        data: models.RecordsRead
        sentence = data.content
        wordcloud.update(sentence)
    imageData = wordcloud.save()
    return MessageSegment.image(f"base64://{b64encode(imageData).decode()}")


@on_command("statistics", aliases=("统计",), permission=SUPERUSER)
@processSession
@SyncToAsync
def _(session: CommandSession):
    session.send("开始生成统计")
    latestTime = datetime.datetime.now() - DELTA_TIME
    frameMaker = DataFrameMaker({"date": str, "time": float})
    messageIter = messageGenterator(
        group_id=session.ctx["group_id"], latestTime=latestTime
    )
    for data in messageIter:
        date = str(data.time.date())
        time = _time2Int(data.time.time())
        frameMaker.update({"date": date, "time": time})
    imageData = Chart.chatFrequency(frameMaker.read())
    return MessageSegment.image(f"base64://{b64encode(imageData).decode()}")
