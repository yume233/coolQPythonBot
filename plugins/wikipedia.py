import os

import requests
from nonetrip import CommandSession, on_command
from utils.configsReader import configsReader, copyFileInText
from utils.decorators import CatchRequestsException, SyncToAsync
from utils.manager import PluginManager
from utils.message import processSession
from utils.network import NetworkUtils

__plugin_name__ = "wikipedia"

PluginManager.registerPlugin(__plugin_name__)

CONFIG_PATH = "configs/wikipedia.yml"
DEFAULT_PATH = "configs/default.wikipedia.yml"

if not os.path.isfile(CONFIG_PATH):
    copyFileInText(DEFAULT_PATH, CONFIG_PATH)

CONFIG_READ = Config = configsReader(CONFIG_PATH, DEFAULT_PATH)


@CatchRequestsException(prompt="从维基获取数据出错")
def getWiki(keyword: str) -> dict:
    requestParam = {
        "action": "query",
        "generator": "prefixsearch",
        "gpssearch": keyword,
        "format": "json",
        "prop": "extracts|info",
        "inprop": "url",
        "exintro": "1",
        "explaintext": "1",
        "uselang": "zh-hans",
    }
    result = requests.get(
        CONFIG_READ.apis.wiki, params=requestParam, proxies=NetworkUtils.proxy
    )
    result.raise_for_status()
    return result.json()


@on_command(__plugin_name__, aliases=("维基搜索", "维基"))
@processSession(pluginName=__plugin_name__)
@SyncToAsync
def wikipedia(session: CommandSession):
    keyword = session.get("keyword")
    session.send(f"开始Wiki搜索:{keyword}")
    pages = getWiki(keyword)["query"]["pages"]
    finalResult = {"keyword": keyword, "size": len(pages)}
    finalResult["result"] = []
    for page in pages.values():
        finalResult["result"].append(
            {
                "title": page["title"],
                "introduce": page["extract"],
                "link": NetworkUtils.shortLink([page["fullurl"]])[page["fullurl"]],
            }
        )
    repeatMessage = [
        str(CONFIG_READ.customize.repeat).format(**result)
        for result in finalResult["result"]
    ]
    fullMessage = (
        str(CONFIG_READ.customize.prefix).format(**finalResult)
        + "".join(repeatMessage[: CONFIG_READ.size])
        + str(CONFIG_READ.customize.suffix).format(**finalResult)
    )
    return fullMessage


@wikipedia.args_parser
@processSession
@SyncToAsync
def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause("请输入搜索关键词")
    session.state["keyword"] = strippedArgs
