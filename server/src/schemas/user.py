from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from schemas.base import BaseFilterParams


class UserFilterParams(BaseFilterParams):
    username: str | None = None
    email: EmailStr | None = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    balance: Decimal
    locked_balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None


class TopUpRequest(BaseModel):
    amount: Decimal
