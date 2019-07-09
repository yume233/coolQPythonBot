from nonebot import CommandSession, MessageSegment, on_command

from .config import *


@on_command('donate',aliases=('捐赠','充钱'))
async def _(session:CommandSession):
    sendMsg = [str(MessageSegment.image(singleImg)) for singleImg in DONATE_IMAGE_LIST]
    sendMsg.append(DONATE_SUFFIX)
    await session.send('\n'.join(sendMsg))

@on_command('help',aliases=('帮助','功能'))
async def botHelp(session:CommandSession):
    sendMsg = HELP_TEXT
    await session.send(sendMsg,at_sender=True)
