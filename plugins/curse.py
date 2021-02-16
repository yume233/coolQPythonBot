import requests
from nonetrip import CommandSession, on_command
from nonetrip.permission import GROUP_MEMBER, check_permission
from utils.decorators import (
    AsyncToSync,
    CatchRequestsException,
    SyncToAsync,
    WithKeyword,
)
from utils.message import processSession


@CatchRequestsException(retries=3, prompt="嘴臭不出来了")
def getCurseContent(min: bool = False):
    r = requests.get(
        "https://nmsl.shadiao.app/api.php", params=({"level": "min"} if min else {})
    )
    r.raise_for_status()
    return "\u200b".join(r.text)


@on_command("curse", aliases=("对线", "口吐芬芳", "嘴臭"))
@WithKeyword("和机器人对线", command="curse")
@processSession
@SyncToAsync
def _(session: CommandSession):
    isMin = AsyncToSync(check_permission)(session.bot, session.ctx, GROUP_MEMBER)
    return getCurseContent(min=isMin)
