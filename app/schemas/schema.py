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

class HealthLogResponse(BaseModel):
    id: int
    status_code: int | None
    response_time: float | None
    is_healthy: bool
    checked_at: datetime

    class Config:
        from_attributes = True