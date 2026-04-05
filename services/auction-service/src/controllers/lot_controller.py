import uuid
from fastapi import APIRouter, Query

from api.dependencies import CurrentUserId, LotServiceDep, PaginationParamsDep, LotFilterParamsDep
from schemas.lot import LotCreateRequest, LotUpdateRequest, LotResponse
from schemas.base import PaginatedResponse, Meta

router = APIRouter()


@router.get("", response_model=PaginatedResponse[LotResponse])
async def get_lots(
    lot_service: LotServiceDep,
    pagination: PaginationParamsDep,
    filters: LotFilterParamsDep,
    auction_id: uuid.UUID = Query(...),
):
    items, total = await lot_service.get_by_auction_id(auction_id, filters, pagination)
    return PaginatedResponse(
        items=items,
        meta=Meta(total=total, page=pagination.page, limit=pagination.limit),
    )


@router.post("", response_model=LotResponse)
async def create_lot(
    data: LotCreateRequest,
    user_id: CurrentUserId,
    lot_service: LotServiceDep,
):
    return await lot_service.create(data, user_id)


@router.get("/{lot_id}", response_model=LotResponse)
async def get_lot(
    lot_id: uuid.UUID,
    lot_service: LotServiceDep,
):
    return await lot_service.get_by_id(lot_id)


@router.patch("/{lot_id}", response_model=LotResponse)
async def update_lot(
    lot_id: uuid.UUID,
    data: LotUpdateRequest,
    user_id: CurrentUserId,
    lot_service: LotServiceDep,
):
    return await lot_service.update(lot_id, data, user_id)


@router.delete("/{lot_id}")
async def delete_lot(
    lot_id: uuid.UUID,
    user_id: CurrentUserId,
    lot_service: LotServiceDep,
):
    await lot_service.delete(lot_id, user_id)
    return {"detail": "Lot deleted successfully"}
