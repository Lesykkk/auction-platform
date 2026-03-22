import uuid
from decimal import Decimal
from dataclasses import dataclass

from models.base import UUIDInMemoryMixin, TimeStampInMemoryMixin


@dataclass
class User(UUIDInMemoryMixin, TimeStampInMemoryMixin):
    username: str
    email: str
    hashed_password: str
    balance: Decimal = Decimal("0.0")
    locked_balance: Decimal = Decimal("0.0")
