import uuid
from decimal import Decimal
from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Bid(BaseModel):
    __tablename__ = "bids"

    lot_id: Mapped[uuid.UUID] = mapped_column(index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
