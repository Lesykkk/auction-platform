import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AuctionStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


@dataclass
class Auction:
    title: str
    description: str
    created_by: uuid.UUID
    closes_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: AuctionStatus = AuctionStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
