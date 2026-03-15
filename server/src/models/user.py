import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class User:
    username: str
    email: str
    hashed_password: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    balance: float = 0.0
    locked_balance: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
