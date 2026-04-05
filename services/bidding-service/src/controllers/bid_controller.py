import uuid
from fastapi import APIRouter, Query

from api.dependencies import CurrentUserId, BidServiceDep, PaginationParamsDep
from schemas.bid import BidCreateRequest, BidResponse
from schemas.base import BaseFilterParams, PaginatedResponse, Meta

router = APIRouter()


@router.get("", response_model=PaginatedResponse[BidResponse])
async def get_bids(
    lot_id: uuid.UUID,
    bid_service: BidServiceDep,
    pagination: PaginationParamsDep,
):
    items, total = await bid_service.get_by_lot_id(lot_id, BaseFilterParams(), pagination)
    return PaginatedResponse(
        items=items,
        meta=Meta(total=total, page=pagination.page, limit=pagination.limit),
    )


@router.post("", response_model=BidResponse)
async def place_bid(
    data: BidCreateRequest,
    user_id: CurrentUserId,
    bid_service: BidServiceDep,
):
    return await bid_service.place_bid(data, user_id)
