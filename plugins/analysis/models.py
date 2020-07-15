from typing import Optional, Dict, Any, List

from nonebot.typing import Context_T
from pydantic import BaseModel


class RecordsCreate(BaseModel):
    sender: int
    group: Optional[int] = None
    content: str
    ctx: Context_T


class RecordsRead(BaseModel):
    rid: int
    sender: int
    group: Optional[int]
    time: float
    content: str
    ctx: Context_T


class Users(BaseModel):
    uid: int
    nickname: str
    data: List[Dict[str, Any]]


class Groups(BaseModel):
    gid: int
    name: str
    members: List[Dict[str, Any]]
