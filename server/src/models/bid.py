import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.lot import Lot
    from models.user import User


class Bid(BaseModel):
    __tablename__ = "bids"

    lot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lots.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="bids", lazy="raise")
    lot: Mapped["Lot"] = relationship(back_populates="bids", lazy="raise")
