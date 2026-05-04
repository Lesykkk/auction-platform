from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from schemas.base import BaseFilterParams, Meta

AuctionStatus = Literal["PENDING", "ACTIVE", "CLOSED", "CANCELLED"]
LotStatus = Literal["PENDING", "ACTIVE", "SOLD", "UNSOLD", "CANCELLED"]


class BidCreateRequest(BaseModel):
    lot_id: UUID
    amount: Decimal = Field(gt=0, le=Decimal("999999999999999.99"))


class BidResponse(BaseModel):
    id: UUID
    lot_id: UUID
    user_id: UUID
    amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MyBidResponse(BaseModel):
    id: UUID
    lot_id: UUID
    auction_id: UUID
    user_id: UUID
    amount: Decimal
    current_price: Decimal
    lot_title: str
    lot_status: LotStatus
    auction_title: str
    auction_status: AuctionStatus
    is_locked: bool
    locked_amount: Decimal
    created_at: datetime


class MyBidsSummary(BaseModel):
    total_locked_amount: Decimal


class MyBidsPaginatedResponse(BaseModel):
    items: list[MyBidResponse]
    meta: Meta
    summary: MyBidsSummary
