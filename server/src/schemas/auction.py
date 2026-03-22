from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.auction import AuctionStatus


class AuctionCreateRequest(BaseModel):
    title: str
    description: str
    closes_at: datetime


class AuctionUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    closes_at: datetime | None = None


class AuctionResponse(BaseModel):
    id: UUID
    title: str
    description: str
    user_id: UUID
    status: AuctionStatus
    created_at: datetime
    closes_at: datetime

    model_config = ConfigDict(from_attributes=True)
