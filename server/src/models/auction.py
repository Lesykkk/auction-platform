import uuid
from enum import StrEnum
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, text, Enum as SQLEnum, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.user import User
    from models.lot import Lot


class AuctionStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class Auction(BaseModel):
    __tablename__ = "auctions"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(2000))
    status: Mapped[AuctionStatus] = mapped_column(
        SQLEnum(AuctionStatus), 
        server_default=text("'PENDING'"),
        index=True
    )
    closes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="auctions", lazy="raise")
    lots: Mapped[list["Lot"]] = relationship(
        back_populates="auction", lazy="raise", passive_deletes=True
    )
