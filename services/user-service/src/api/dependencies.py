import uuid
from typing import Annotated, AsyncGenerator
from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_token
from core.database import async_session_maker
from exceptions.handlers import UnauthorizedError
from models.user import User

from repositories.user import UserRepository
from services.auth_service import AuthService
from services.user_service import UserService
from schemas.base import PaginationParams
from schemas.user import UserFilterParams

security = HTTPBearer()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


DbDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_user_repository(db: DbDep) -> UserRepository:
    return UserRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    payload = decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        raise UnauthorizedError("Invalid token")

    user = await user_repo.find_by_id(user_id)
    if not user:
        raise UnauthorizedError("User not found")

    return user


def get_pagination_params(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit)


PaginationParamsDep = Annotated[PaginationParams, Depends(get_pagination_params)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]
UserFilterParamsDep = Annotated[UserFilterParams, Depends()]
