from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SiteBase(BaseModel):
    url: str
    name: str
    is_active: bool = True


class SiteCreate(SiteBase):
    pass


class SiteUpdate(BaseModel):
    url: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class SiteResponse(SiteBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PingLogResponse(BaseModel):
    id: int
    site_id: int
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    is_up: bool
    checked_at: datetime
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}
