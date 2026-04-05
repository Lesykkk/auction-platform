import uuid
from fastapi import APIRouter, Query

from api.dependencies import CurrentUser, BidServiceDep, PaginationParamsDep, BidFilterParamsDep
from schemas.bid import BidCreateRequest, BidResponse
from schemas.base import PaginatedResponse, Meta

router = APIRouter()


@router.get("", response_model=PaginatedResponse[BidResponse])
async def get_bids(
    bid_service: BidServiceDep,
    pagination: PaginationParamsDep,
    filters: BidFilterParamsDep,
    lot_id: uuid.UUID = Query(...),
):
    items, total = await bid_service.get_bids_by_lot_id(lot_id, filters, pagination)
    return PaginatedResponse(
        items=items,
        meta=Meta(total=total, page=pagination.page, limit=pagination.limit),
    )


@router.post("", response_model=BidResponse)
async def place_bid(
    data: BidCreateRequest,
    user: CurrentUser,
    bid_service: BidServiceDep,
):
    return await bid_service.place_bid(data, user)
