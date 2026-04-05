import uuid
from enum import StrEnum
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Numeric, text, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.auction import Auction
    from models.bid import Bid
    from models.payment import Payment


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
        index=True
    )
    winner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)

    # Relationships
    auction: Mapped["Auction"] = relationship(back_populates="lots", lazy="raise")
    bids: Mapped[list["Bid"]] = relationship(
        back_populates="lot", lazy="raise", passive_deletes=True
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="lot", lazy="raise", passive_deletes=True
    )
