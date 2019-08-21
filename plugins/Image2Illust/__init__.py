from nonebot import CommandSession, on_command
from nonebot.permission import GROUP_ADMIN, PRIVATE_FRIEND, SUPERUSER

from utils.customDecorators import SyncToAsync, WithKeyword
from utils.messageProc import processSession
from utils.pluginManager import manager

from .config import Config
from .network import searchImage
from .parse import getCorrectInfo

manager.registerPlugin('illust_search', defaultStatus=False)


@on_command('illust_search', aliases=('以图搜图', '搜图'))
@processSession(pluginName='illust_search')
@WithKeyword('以图搜图', command='illust_search')
@SyncToAsync
def illustSearch(session: CommandSession):
    imageURL = session.get('image')
    session.send('开始以图搜图')
    searchContent = searchImage(imageURL)
    searchParse = getCorrectInfo(searchContent)
    messageRepeat = [
        str(Config.customize.repeat).format(**subject)
        for subject in searchParse['subject']
    ]
    fullMessage = str(Config.customize.prefix).format(**searchParse)\
        + ''.join(messageRepeat[:Config.customize.size])\
        + str(Config.customize.suffix).format(**searchParse)
    return fullMessage


@illustSearch.args_parser
@processSession(pluginName='illust_search')
@SyncToAsync
def _(session: CommandSession):
    if session.current_arg_images:
        session.state['image'] = session.current_arg_images[0]
    else:
        session.pause('请发送一张图片来进行搜索')


@on_command('illust_search_enable',
            aliases=('启用搜图', '打开以图搜图'),
            permission=GROUP_ADMIN | SUPERUSER | PRIVATE_FRIEND)
@processSession
@SyncToAsync
def _(session: CommandSession):
    manager.settings('illust_search', ctx=session.ctx).status = True
    return '搜图功能已启用', False


@on_command('illust_search_disable',
            aliases=('禁用搜图', '关闭以图搜图'),
            permission=GROUP_ADMIN | SUPERUSER | PRIVATE_FRIEND)
@processSession
@SyncToAsync
def _(session: CommandSession):
    manager.settings('illust_search', ctx=session.ctx).status = False
    return '搜图功能已禁用', False
