"""
Internal endpoints called by other microservices (auction-service, bidding-service).
These routes are accessible within the Docker network only (not exposed via nginx).
"""
import uuid
from fastapi import APIRouter, Depends

from api.dependencies import get_user_repository, get_db_session, DbDep
from repositories.user import UserRepository
from services.user_service import UserService
from schemas.user import UserResponse, AdjustBalanceRequest

router = APIRouter()


def get_user_service_internal(db: DbDep) -> UserService:
    return UserService(UserRepository(db))


UserServiceInternalDep = UserService


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_internal(
    user_id: uuid.UUID,
    db: DbDep,
):
    """Return user by ID. Called internally by other services to validate user exists."""
    service = UserService(UserRepository(db))
    return await service.get_by_id(user_id)


@router.post("/users/{user_id}/adjust-balance", response_model=UserResponse)
async def adjust_balance_internal(
    user_id: uuid.UUID,
    data: AdjustBalanceRequest,
    db: DbDep,
):
    """
    Adjust user balance and/or locked_balance.
    Called by bidding-service when placing bids or settling auctions.
    """
    service = UserService(UserRepository(db))
    return await service.adjust_balance(user_id, data)
