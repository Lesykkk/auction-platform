import uuid
from datetime import datetime
from sqlalchemy import text, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        server_default=text("uuidv7()")
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    __abstract__ = True
