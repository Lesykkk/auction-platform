from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    balance: Decimal
    locked_balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None


class TopUpRequest(BaseModel):
    amount: Decimal
