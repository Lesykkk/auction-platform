import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class LotStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    UNSOLD = "UNSOLD"
    CANCELLED = "CANCELLED"


@dataclass
class Lot:
    auction_id: uuid.UUID
    title: str
    description: str
    starting_price: float
    min_bid_increment: float
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    current_price: float = 0.0
    status: LotStatus = LotStatus.PENDING
    winner_id: uuid.UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.current_price == 0.0:
            self.current_price = self.starting_price
