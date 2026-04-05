from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from schemas.base import BaseFilterParams


class BidFilterParams(BaseFilterParams):
    pass


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
