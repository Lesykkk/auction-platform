from fastapi import APIRouter, Depends

from api.dependencies import get_current_user, get_bid_service
from models.user import User
from schemas.bid import BidCreateRequest, BidResponse
from services.bid_service import BidService

router = APIRouter()


@router.post("", response_model=BidResponse)
async def place_bid(
    data: BidCreateRequest,
    user: User = Depends(get_current_user),
    bid_service: BidService = Depends(get_bid_service),
):
    return await bid_service.place_bid(data, user)
