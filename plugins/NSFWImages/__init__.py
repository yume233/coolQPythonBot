import random
from secrets import token_hex

from nonebot import CommandSession, MessageSegment, on_command
from nonebot.command.argfilter.extractors import extract_numbers
from nonebot.permission import GROUP_ADMIN, PRIVATE_FRIEND, SUPERUSER

from utils.decorators import SyncToAsync, WithKeyword
from utils.manager import PluginManager, nameJoin
from utils.message import processSession

from .config import Config
from .network import downloadImage, downloadMultiImage, getImageList

__plugin_name__ = 'NSFWImages'
OPERATING_METHOD = nameJoin(__plugin_name__, 'ops')
POWER_GROUP = (GROUP_ADMIN | PRIVATE_FRIEND | SUPERUSER)

PluginManager.registerPlugin(__plugin_name__, defaultStatus=False)
PluginManager.registerPlugin(OPERATING_METHOD)


@on_command(__plugin_name__, aliases=('setu', '涩图', '色图'))
@processSession(pluginName=__plugin_name__)
@WithKeyword('来一张涩图', command=__plugin_name__)
@SyncToAsync
def NSFWImage(session: CommandSession):
    rank: str = session.get_optional('rank', Config.send.default)
    pictureCount: int = session.get_optional('num', 1)
    pictureCount = pictureCount if pictureCount <= Config.send.size else Config.send.size
    session.send(f'{rank.upper()}级涩图加载中,将连续发送最多{pictureCount}张')
    imageList = getImageList()
    assert imageList
    imageList = [
        i['sample_url'] for i in random.shuffle(
            [i for i in imageList if i['rating'].upper() in rank.upper()])
    ][:pictureCount]
    images = downloadMultiImage(imageList)
    imageRes = [str(MessageSegment.image(i)) for i in images.values()]
    return '\n'.join(imageRes)


@NSFWImage.args_parser
@processSession(pluginName=__plugin_name__)
@SyncToAsync
def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        return
    numberArgs = extract_numbers(strippedArgs)
    splicedArgs = strippedArgs.split(' ')
    if numberArgs:
        session.state['num'] = int(numberArgs[0])
    for perArg in splicedArgs:
        if not perArg.isalpha(): continue
        rankList = ['S', 'Q', 'E']
        avaliableRank = ''.join(
            [rank for rank in rankList if rank.upper() in perArg])
    if avaliableRank:
        session.state['rank'] = avaliableRank


@on_command(f'{OPERATING_METHOD}_enable',
            aliases=('启用涩图', '打开涩图'),
            permission=POWER_GROUP)
@processSession(pluginName=OPERATING_METHOD)
@SyncToAsync
def enable(session: CommandSession):
    key: str = session.get('key')
    realKey: str = PluginManager.settings(pluginName=OPERATING_METHOD,
                                          ctx=session.ctx).settings.get(
                                              'key', '')
    if key.upper() == realKey.upper():
        PluginManager.settings(pluginName=__plugin_name__,
                               ctx=session.ctx).status = True
        return '涩图功能已启用', False
    else:
        return '此激活密钥无效', False


@enable.args_parser
@processSession(pluginName=OPERATING_METHOD)
@SyncToAsync
def _(session: CommandSession):
    from re import search
    strippedArgs = session.current_arg_text.strip()
    matchObj = search(r'[a-fA-F0-9]{8,40}', strippedArgs)
    if not matchObj: session.pause('请输入激活密钥')
    session.state['key'] = str(matchObj.group(0)).upper()


@on_command(f'{OPERATING_METHOD}_disable',
            aliases=('禁用涩图', '关闭涩图'),
            permission=POWER_GROUP)
@processSession(pluginName=OPERATING_METHOD)
@SyncToAsync
def _(session: CommandSession):
    PluginManager.settings(pluginName=__plugin_name__,
                           ctx=session.ctx).status = False
    return '涩图功能已禁用'


@on_command(f'{OPERATING_METHOD}_publish',
            aliases=('生成涩图密钥', ),
            permission=SUPERUSER)
@processSession(pluginName=OPERATING_METHOD)
@SyncToAsync
def _(session: CommandSession):
    key = token_hex(8).upper()
    PluginManager.settings(pluginName=OPERATING_METHOD,
                           ctx=session.ctx).settings = {
                               'key': key
                           }
    return f'涩图密钥已经生成,为{key}'


@on_command(f'{OPERATING_METHOD}_back',
            aliases=('回收涩图密钥', ),
            permission=SUPERUSER)
@processSession(pluginName=OPERATING_METHOD)
@SyncToAsync
def _(session: CommandSession):
    getKey = PluginManager.settings(pluginName=OPERATING_METHOD,
                                    ctx=session.ctx).settings.get(
                                        'key',
                                        token_hex(8).upper())
    key = ''.join([chr(ord(i) + 10) for i in list(getKey)])
    PluginManager.settings(pluginName=OPERATING_METHOD,
                           ctx=session.ctx).settings = {
                               'key': key
                           }
    return f'涩图密钥已被回收'
