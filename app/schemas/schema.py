from pydantic import BaseModel, HttpUrl
from datetime import datetime


class APICreate(BaseModel):
    name: str
    url: HttpUrl


class APIResponse(BaseModel):
    id: int
    name: str
    url: HttpUrl
    created_at: datetime

    class Config:
        from_attributes = True