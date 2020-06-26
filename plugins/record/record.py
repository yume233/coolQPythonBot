import asyncio
from typing import Any, Dict, List

from nonebot import NLPSession, get_bot, on_natural_language, scheduler
from nonebot.command.argfilter.extractors import extract_text
from nonebot.exceptions import CQHttpError
from nonebot.log import logger

from utils.decorators import SyncToAsync
from utils.message import processSession
from utils.objects import callModuleAPI
from utils.exception import ExceptionProcess

from . import models
from .DAO import RecordDAO

DatabaseIO = RecordDAO()

on_startup = get_bot().server_app.before_serving


@scheduler.scheduled_job("interval", minutes=10)
@SyncToAsync
def saveDetail():
    logger.info("Refreshing detail of users and groups.")
    groupList: List[Dict[str, Any]] = callModuleAPI("get_group_list")
    groupData: Dict[int, Dict[str, Any]] = {}
    usersData: Dict[int, List[Dict[str, Any]]] = {}
    for group in groupList:
        groupID: int = group["group_id"]
        groupName: str = group["group_name"]
        data = callModuleAPI(
            "get_group_member_list", params={"group_id": groupID}, ignoreError=True
        )
        if not data:
            continue
        groupData[groupID] = data
        DatabaseIO.groupCreate(
            models.Groups(gid=groupID, name=groupName, members=data), updateIfExist=True
        )
        for user in data:
            userID: int = user["user_id"]
            userGroups = usersData.get(userID, [])
            for i in userGroups:
                if i["group_id"] == groupID:
                    userGroups.remove(i)
            userGroups.append(user)
            usersData[userID] = userGroups
    for userID, user in usersData.items():
        DatabaseIO.userCreate(
            models.Users(uid=userID, nickname=user[0]["nickname"], data=user),
            updateIfExist=True,
        )


@on_startup
async def startupHook():
    async def wrapper():
        while True:
            await asyncio.sleep(1)
            try:
                info = await get_bot().call_action("get_login_info")
            except CQHttpError:
                pass
            else:
                break
        logger.debug(f"Program API started successfully, account info: {info}")
        await saveDetail()

    get_bot().loop.create_task(wrapper())


@on_natural_language(
    only_to_me=False, only_short_message=False, allow_empty_message=True
)
@SyncToAsync
def recordChat(session: NLPSession):
    content = extract_text(session.ctx["message"])
    ctx = session.ctx.copy()
    sender = session.ctx["user_id"]
    group = session.ctx.get("group_id")
    data = models.RecordsCreate(sender=sender, group=group, content=content, ctx=ctx)

    try:
        result = DatabaseIO.recordCreate(data)
    except Exception as e:
        traceID = ExceptionProcess.catch()
        logger.warning(
            f"Chat record {data} failed to storage due to {e} (Traceback ID:{traceID})."
        )
    else:
        logger.debug(
            f"Chat record {result} has been storaged to database successfully."
        )
