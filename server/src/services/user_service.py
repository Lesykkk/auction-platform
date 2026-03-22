from decimal import Decimal
from models.user import User
from repositories.user_repository import UserRepository
from schemas.user import UserUpdateRequest, TopUpRequest
from exceptions.handlers import ConflictError, BusinessLogicError


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_me(self, user: User) -> User:
        return user

    async def update_me(self, user: User, data: UserUpdateRequest) -> User:
        if data.username is not None:
            existing = await self.user_repository.get_by_username(data.username)
            if existing and existing.id != user.id:
                raise ConflictError("Username already taken")
            user.username = data.username

        if data.email is not None:
            existing = await self.user_repository.get_by_email(data.email)
            if existing and existing.id != user.id:
                raise ConflictError("Email already registered")
            user.email = data.email

        return await self.user_repository.save(user)

    async def top_up_balance(self, user: User, data: TopUpRequest) -> User:
        if data.amount <= Decimal("0.0"):
            raise BusinessLogicError("Amount must be positive")

        user.balance += data.amount
        return await self.user_repository.save(user)
