from fastapi import APIRouter, Depends

from api.dependencies import get_current_user, get_user_service
from models.user import User
from schemas.user import UserResponse, UserUpdateRequest, TopUpRequest
from services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
):
    return user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdateRequest,
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_me(user, data)


@router.post("/me/top-up", response_model=UserResponse)
async def top_up(
    data: TopUpRequest,
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.top_up_balance(user, data)
