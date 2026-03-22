import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(kw_only=True)
class UUIDInMemoryMixin:
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(kw_only=True)
class TimeStampInMemoryMixin:
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
