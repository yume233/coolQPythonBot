from datetime import datetime
from typing import Any, Dict, List, Optional

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
    time: datetime
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
