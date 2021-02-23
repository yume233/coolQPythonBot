from nonetrip import CommandSession, on_command
from nonetrip.permission import GROUP
from utils.decorators import SyncToAsync
from utils.message import processSession

__plugin_name__ = "rss_notice"


@on_command(__plugin_name__, aliases=("rss", "RSS", "RSS订阅"), permission=GROUP)
@processSession
@SyncToAsync
def _(session: CommandSession):
    return "该功能由第三方插件实现, 使用方式请参考 https://git.io/Jt79w"
