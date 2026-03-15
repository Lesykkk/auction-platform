from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.lot import LotStatus


class LotCreateRequest(BaseModel):
    title: str
    description: str
    starting_price: float
    min_bid_increment: float


class LotUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    starting_price: float | None = None
    min_bid_increment: float | None = None


class LotResponse(BaseModel):
    id: UUID
    auction_id: UUID
    title: str
    description: str
    starting_price: float
    min_bid_increment: float
    current_price: float
    status: LotStatus
    winner_id: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
