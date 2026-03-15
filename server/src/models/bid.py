import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Bid:
    lot_id: uuid.UUID
    bidder_id: uuid.UUID
    amount: float
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
