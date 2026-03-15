from fastapi import APIRouter, Depends, Request, Response

from api.dependencies import get_auth_service
from exceptions.handlers import UnauthorizedError
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from schemas.user import UserResponse
from services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register(data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    token_response, refresh_token = await auth_service.login(data)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedError("Refresh token not found")

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
