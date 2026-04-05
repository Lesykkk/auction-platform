import uuid
from enum import StrEnum
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, text, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class LotStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    UNSOLD = "UNSOLD"
    CANCELLED = "CANCELLED"


class Lot(BaseModel):
    __tablename__ = "lots"

    auction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auctions.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(2000))
    starting_price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    min_bid_increment: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    current_price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    status: Mapped[LotStatus] = mapped_column(
        SQLEnum(LotStatus),
        server_default=text("'PENDING'"),
        index=True,
    )
    winner_id: Mapped[uuid.UUID | None] = mapped_column(index=True, nullable=True)
