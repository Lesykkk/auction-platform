import uuid
from enum import StrEnum
from decimal import Decimal
from sqlalchemy import Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class PaymentStatus(StrEnum):
    COMPLETED = "COMPLETED"
    REFUNDED = "REFUNDED"


class Payment(BaseModel):
    __tablename__ = "payments"

    lot_id: Mapped[uuid.UUID] = mapped_column(index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), index=True)
