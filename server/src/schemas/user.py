from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    balance: float
    locked_balance: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None


class TopUpRequest(BaseModel):
    amount: float
