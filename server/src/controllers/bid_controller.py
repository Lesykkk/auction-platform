import uuid
from fastapi import APIRouter, Query

from api.dependencies import CurrentUser, BidServiceDep
from schemas.bid import BidCreateRequest, BidResponse

router = APIRouter()


@router.get("", response_model=list[BidResponse])
async def get_bids(
    bid_service: BidServiceDep,
    lot_id: uuid.UUID = Query(...),
):
    return await bid_service.get_bids_by_lot(lot_id)


@router.post("", response_model=BidResponse)
async def place_bid(
    data: BidCreateRequest,
    user: CurrentUser,
    bid_service: BidServiceDep,
):
    return await bid_service.place_bid(data, user)
