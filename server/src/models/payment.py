import uuid
from enum import StrEnum
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.lot import Lot
    from models.user import User


class PaymentStatus(StrEnum):
    COMPLETED = "COMPLETED"
    REFUNDED = "REFUNDED"


class Payment(BaseModel):
    __tablename__ = "payments"

    lot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lots.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), index=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="payments", lazy="raise")
    lot: Mapped["Lot"] = relationship(back_populates="payments", lazy="raise")