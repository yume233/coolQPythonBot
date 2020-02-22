from time import time
from typing import List

from nonebot import CommandSession, on_command
from nonebot.permission import GROUP_ADMIN, SUPERUSER

from utils.decorators import SyncToAsync
from utils.manager import PluginManager
from utils.message import processSession
from utils.objects import callModuleAPI

__plugin_name__ = 'broadcast'
PluginManager(__plugin_name__)
POWER_GROUP = SUPERUSER | GROUP_ADMIN


@on_command('broadcast', aliases=('广播', ), permission=SUPERUSER)
@processSession
@SyncToAsync
def broadcast(session: CommandSession):
    broadcastContent = session.get('content')
    session.send(f'开始广播消息,内容如下:\n{broadcastContent}')
    beginTime = time()
    groupsList: List[int] = [
        i['group_id'] for i in callModuleAPI('get_group_list')
    ]
    totalSend = 0
    for groupID in groupsList:
        enabled = PluginManager._getSettings(__plugin_name__,
                                             type='group',
                                             id=groupID).status
        if not enabled:
            continue
        sendParams = {'group_id': groupID, 'message': broadcastContent}
        callModuleAPI('send_msg', params=sendParams)
        totalSend += 1
    return (f'消息广播完成,已广播到{totalSend}个群聊\n耗时{time() - beginTime:.3f}s')


@broadcast.args_parser
@processSession
@SyncToAsync
def _(session: CommandSession):
    strippedArgs = session.current_arg.strip()
    if not strippedArgs:
        session.pause('请输入广播内容')
    session.state['content'] = strippedArgs


@on_command('block_broadcast', aliases=('屏蔽广播', ), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, ctx=session.ctx).status = False
    return '群聊广播已被屏蔽,您将不会再收到来自开发者的广播'


@on_command('receive_broadcast', aliases=('接收广播', ), permission=POWER_GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(__plugin_name__, ctx=session.ctx).status = True
    return '群聊广播已被启用,您将会收到来自开发者的广播'
