import uuid
from decimal import Decimal
from dataclasses import dataclass

from models.base import UUIDInMemoryMixin, TimeStampInMemoryMixin


@dataclass
class Bid(UUIDInMemoryMixin, TimeStampInMemoryMixin):
    lot_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal

