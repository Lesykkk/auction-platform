import uuid
from models.user import User
from repositories.user_repository import UserRepository
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from exceptions.handlers import ConflictError, UnauthorizedError


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(self, data: RegisterRequest) -> User:
        existing_username = await self.user_repository.get_by_username(data.username)
        if existing_username:
            raise ConflictError("Username already taken")

        existing_email = await self.user_repository.get_by_email(data.email)
        if existing_email:
            raise ConflictError("Email already registered")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return await self.user_repository.create(user)

    async def login(self, data: LoginRequest) -> tuple[TokenResponse, str]:
        user = await self.user_repository.get_by_username(data.username)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid username or password")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        token_response = TokenResponse(access_token=access_token)
        return token_response, refresh_token

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token payload")

        try:
            parsed_uuid = uuid.UUID(user_id)
        except ValueError:
            raise UnauthorizedError("Invalid user ID")

        user = await self.user_repository.get(parsed_uuid)
        if not user:
            raise UnauthorizedError("User not found")

        access_token = create_access_token({"sub": str(user.id)})
        return TokenResponse(access_token=access_token)
