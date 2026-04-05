from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.payment import PaymentStatus
from schemas.base import BaseFilterParams


class PaymentFilterParams(BaseFilterParams):
    status: PaymentStatus | None = None


class PaymentResponse(BaseModel):
    id: UUID
    lot_id: UUID
    user_id: UUID
    amount: Decimal
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
