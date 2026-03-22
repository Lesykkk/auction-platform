import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from models.base import UUIDInMemoryMixin, TimeStampInMemoryMixin


class AuctionStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


@dataclass
class Auction(UUIDInMemoryMixin, TimeStampInMemoryMixin):
    title: str
    description: str
    user_id: uuid.UUID
    closes_at: datetime
    status: AuctionStatus = AuctionStatus.PENDING
