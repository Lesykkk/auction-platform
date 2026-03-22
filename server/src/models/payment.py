import uuid
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

from models.base import UUIDInMemoryMixin, TimeStampInMemoryMixin


class PaymentStatus(str, Enum):
    COMPLETED = "COMPLETED"
    REFUNDED = "REFUNDED"


@dataclass
class Payment(UUIDInMemoryMixin, TimeStampInMemoryMixin):
    lot_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    status: PaymentStatus
