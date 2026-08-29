from datetime import datetime
from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: str
    title: str
    body: str
    createdAt: datetime
    read: bool


class NotificationUpdate(BaseModel):
    read: bool
