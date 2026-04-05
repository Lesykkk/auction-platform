from decimal import Decimal

from core.security import hash_password
from exceptions.handlers import ConflictError, BusinessLogicError
from models.user import User
from repositories.in_memory.user import UserRepository
from schemas.user import UserUpdateRequest, TopUpRequest, RegisterRequest


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(self, data: RegisterRequest) -> User:
        if await self.user_repository.find_by_username(data.username):
            raise ConflictError("Username already taken")
        if await self.user_repository.find_by_email(data.email):
            raise ConflictError("Email already registered")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return await self.user_repository.save(user)

    async def update_me(self, user: User, data: UserUpdateRequest) -> User:
        if data.username is not None:
            existing = await self.user_repository.find_by_username(data.username)
            if existing and existing.id != user.id:
                raise ConflictError("Username already taken")
            user.username = data.username

        if data.email is not None:
            existing = await self.user_repository.find_by_email(data.email)
            if existing and existing.id != user.id:
                raise ConflictError("Email already registered")
            user.email = data.email

        return await self.user_repository.save(user)

    async def top_up_balance(self, user: User, data: TopUpRequest) -> User:
        if data.amount <= Decimal("0.0"):
            raise BusinessLogicError("Amount must be positive")
        user.balance += data.amount
        return await self.user_repository.save(user)
