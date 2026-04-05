import uuid
from enum import StrEnum
from datetime import datetime
from sqlalchemy import ForeignKey, text, Enum as SQLEnum, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


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
        index=True,
    )
    closes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
