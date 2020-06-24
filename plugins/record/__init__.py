from nonebot import (
    CommandSession,
    NLPSession,
    on_command,
    on_natural_language,
    scheduler,
)
from nonebot.command.argfilter.extractors import extract_text
from nonebot.log import logger

from utils.decorators import SyncToAsync
from utils.message import processSession


from . import models
from .DAO import RecordDAO

DatabaseIO = RecordDAO()


@on_natural_language(
    only_to_me=False, only_short_message=False, allow_empty_message=True
)
@SyncToAsync
def _(session: NLPSession):
    content = extract_text(session.ctx["message"])
    ctx = session.ctx.copy()
    sender = session.ctx["user_id"]
    group = session.ctx.get("group_id")

    data = models.RecordsCreate(sender=sender, group=group, content=content, ctx=ctx)
    result = DatabaseIO.recordCreate(data)

    logger.debug(f"Chat record {result.__repr__()} has been saved to database")

