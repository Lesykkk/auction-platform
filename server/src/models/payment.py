import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class PaymentStatus(str, Enum):
    COMPLETED = "COMPLETED"
    REFUNDED = "REFUNDED"


@dataclass
class Payment:
    lot_id: uuid.UUID
    user_id: uuid.UUID
    amount: float
    status: PaymentStatus
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
