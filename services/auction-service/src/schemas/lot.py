from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.lot import LotStatus
from schemas.base import BaseFilterParams


class LotFilterParams(BaseFilterParams):
    status: LotStatus | None = None


class LotCreateRequest(BaseModel):
    auction_id: UUID
    title: str = Field(min_length=5, max_length=255)
    description: str = Field(min_length=10, max_length=2000)
    starting_price: Decimal = Field(gt=0, le=Decimal("999999999999999.99"))
    min_bid_increment: Decimal = Field(gt=0, le=Decimal("999999999999999.99"))


class LotUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=5, max_length=255)
    description: str | None = Field(None, min_length=10, max_length=2000)
    starting_price: Decimal | None = Field(None, gt=0, le=Decimal("999999999999999.99"))
    min_bid_increment: Decimal | None = Field(None, gt=0, le=Decimal("999999999999999.99"))


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
