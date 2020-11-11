import json
from html import unescape as htmlUnescape
from re import compile as compileRegexp

from nonebot import (
    CommandSession,
    IntentCommand,
    MessageSegment,
    NLPSession,
    logger,
    on_command,
    on_natural_language,
)

from utils.decorators import SyncToAsync
from utils.message import processSession

MATCH_RICH_TEXT = compileRegexp(r"\[CQ:rich,data=(\{.+\})\]")
REPLY_FORMAT = """
{preview}
{prompt} - {desc}

{link}
"""


def parse(data: str) -> dict:
    dataLoad = json.loads(data)
    link = ""
    perview = ""  # noqa: F841
    assert "desc" in dataLoad
    assert "prompt" in dataLoad
    assert "meta" in dataLoad
    for detail in dataLoad["meta"].values():
        if "qqdocurl" in detail:
            link = detail["qqdocurl"]
        if "preview" in detail:
            preview = detail["preview"]
    return {
        "desc": dataLoad["desc"],
        "prompt": dataLoad["prompt"],
        "link": link,
        "preview": MessageSegment.image(preview) if preview else preview,
    }


@on_command("miniprogram_extract")
@processSession
@SyncToAsync
def _(session: CommandSession):
    data = session.state["data"]
    parsed = parse(data)
    logger.debug(f"Parsed miniprogram {parsed}")
    return REPLY_FORMAT.format(**parsed)


@on_natural_language(
    only_short_message=False, only_to_me=False, allow_empty_message=True
)
@SyncToAsync
def _(session: NLPSession):
    message = htmlUnescape(str(session.event.message))
    searchResult = MATCH_RICH_TEXT.search(message)
    if not searchResult:
        return
    logger.debug(f"Catch miniprogram {searchResult}")
    return IntentCommand(
        100, name="miniprogram_extract", args={"data": searchResult.group(1)}
    )
