from typing import Annotated
from fastapi import APIRouter, Cookie, Response

from api.dependencies import AuthServiceDep
from core.config import get_settings
from exceptions.handlers import UnauthorizedError
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from schemas.user import UserResponse

settings = get_settings()

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    data: RegisterRequest,
    auth_service: AuthServiceDep,
):
    return await auth_service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    response: Response,
    auth_service: AuthServiceDep,
):
    token_response, refresh_token = await auth_service.login(data)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    auth_service: AuthServiceDep,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if refresh_token is None:
        raise UnauthorizedError("Missing refresh token")
    return await auth_service.refresh(refresh_token)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return {"detail": "Logged out successfully"}
