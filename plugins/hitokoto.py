import httpx
from nonebot.typing import Bot, Event
from utils.manager import FeaturesRoot

PluginRoot = FeaturesRoot("hitokoto", description="The Hitokoto Model")

hitokoto = PluginRoot.feature("hitokoto")

hitokoto_matcher = hitokoto.matcher.on_command(cmd="一言")


@hitokoto_matcher.handle()
async def handler(bot: Bot, event: Event, state: dict):
    await bot.send(event, f"Hello,World!\n{state}")
