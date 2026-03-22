import uuid
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

from models.base import UUIDInMemoryMixin, TimeStampInMemoryMixin


class LotStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    UNSOLD = "UNSOLD"
    CANCELLED = "CANCELLED"


@dataclass
class Lot(UUIDInMemoryMixin, TimeStampInMemoryMixin):
    auction_id: uuid.UUID
    title: str
    description: str
    starting_price: Decimal
    min_bid_increment: Decimal
    current_price: Decimal = Decimal("0.0")
    status: LotStatus = LotStatus.PENDING
    winner_id: uuid.UUID | None = None


    def __post_init__(self):
        if self.current_price == Decimal("0.0"):
            self.current_price = self.starting_price
