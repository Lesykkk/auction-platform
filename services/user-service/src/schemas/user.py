from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from schemas.base import BaseFilterParams


class UserFilterParams(BaseFilterParams):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = Field(None, max_length=255)


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    balance: Decimal
    locked_balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class UserUpdateRequest(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = Field(None, max_length=255)


class TopUpRequest(BaseModel):
    amount: Decimal = Field(gt=0, le=Decimal("999999999999999.99"))


class AdjustBalanceRequest(BaseModel):
    delta_balance: Decimal = Field(default=Decimal("0"))
    delta_locked: Decimal = Field(default=Decimal("0"))
