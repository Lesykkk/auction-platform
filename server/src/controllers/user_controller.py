from fastapi import APIRouter
from api.dependencies import CurrentUser, UserServiceDep
from schemas.user import UserResponse, UserUpdateRequest, TopUpRequest

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: CurrentUser,
):
    return user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdateRequest,
    user: CurrentUser,
    user_service: UserServiceDep,
):
    return await user_service.update_me(user, data)


@router.post("/me/top-up", response_model=UserResponse)
async def top_up(
    data: TopUpRequest,
    user: CurrentUser,
    user_service: UserServiceDep,
):
    return await user_service.top_up_balance(user, data)
