from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Numeric, text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.auction import Auction
    from models.bid import Bid
    from models.payment import Payment


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        server_default=text("0"),
        default=Decimal("0.0")
    )
    locked_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        server_default=text("0"),
        default=Decimal("0.0")
    )

    # Relationships
    auctions: Mapped[list["Auction"]] = relationship(
        back_populates="user", lazy="raise", passive_deletes=True
    )
    bids: Mapped[list["Bid"]] = relationship(
        back_populates="user", lazy="raise", passive_deletes=True
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="user", lazy="raise", passive_deletes=True
    )
