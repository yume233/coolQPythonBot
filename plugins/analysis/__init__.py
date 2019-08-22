from base64 import b64encode

from nonebot import CommandSession, MessageSegment, on_command
from nonebot.permission import GROUP_ADMIN, PRIVATE, SUPERUSER

from utils.customDecorators import SyncToAsync
from utils.messageProc import processSession

from .data import genWordCloud


@on_command('wordcloud', aliases=('词云',),permission=GROUP_ADMIN | SUPERUSER | PRIVATE)
@processSession
@SyncToAsync
def wordcloud(session: CommandSession):
    sessType = session.ctx['message_type'] \
            if session.ctx['message_type'] == 'group' else 'user'
    sessID = session.ctx['group_id'] \
            if sessType == 'group' else session.ctx['user_id']
    session.send('开始生成词云')
    genResult = genWordCloud(sessID,sessType)
    fileEncoded = b64encode(genResult).decode()
    print(fileEncoded[:100])
    return MessageSegment.image(f'base64://{fileEncoded}')
