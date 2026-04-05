import uuid
from core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from exceptions.handlers import UnauthorizedError
from repositories.user import UserRepository
from schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def login(self, data: LoginRequest) -> tuple[TokenResponse, str]:
        user = await self.user_repository.find_by_username(data.username)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid username or password")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        return TokenResponse(access_token=access_token), refresh_token

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

        user = await self.user_repository.find_by_id(parsed_uuid)
        if not user:
            raise UnauthorizedError("User not found")

        access_token = create_access_token({"sub": str(user.id)})
        return TokenResponse(access_token=access_token)
