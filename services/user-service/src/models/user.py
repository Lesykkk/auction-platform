from decimal import Decimal
from sqlalchemy import Numeric, text, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        server_default=text("0"),
        default=Decimal("0.0"),
    )
    locked_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        server_default=text("0"),
        default=Decimal("0.0"),
    )
