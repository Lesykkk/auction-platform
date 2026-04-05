from datetime import datetime
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.auction import AuctionStatus
from schemas.base import BaseFilterParams


class AuctionFilterParams(BaseFilterParams):
    status: AuctionStatus | None = None


class AuctionCreateRequest(BaseModel):
    title: str = Field(min_length=5, max_length=255)
    description: str = Field(min_length=10, max_length=2000)
    closes_at: datetime


class AuctionUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=5, max_length=255)
    description: str | None = Field(None, min_length=10, max_length=2000)
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
