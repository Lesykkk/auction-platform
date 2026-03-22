from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.lot import LotStatus


class LotCreateRequest(BaseModel):
    auction_id: UUID
    title: str
    description: str
    starting_price: Decimal
    min_bid_increment: Decimal


class LotUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    starting_price: Decimal | None = None
    min_bid_increment: Decimal | None = None


class LotResponse(BaseModel):
    id: UUID
    auction_id: UUID
    title: str
    description: str
    starting_price: Decimal
    min_bid_increment: Decimal
    current_price: Decimal
    status: LotStatus
    winner_id: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
