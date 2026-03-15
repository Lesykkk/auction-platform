from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BidCreateRequest(BaseModel):
    lot_id: UUID
    amount: float


class BidResponse(BaseModel):
    id: UUID
    lot_id: UUID
    bidder_id: UUID
    amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
