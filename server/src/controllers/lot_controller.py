import uuid
from fastapi import APIRouter, Query

from api.dependencies import CurrentUser, LotServiceDep
from schemas.lot import LotCreateRequest, LotUpdateRequest, LotResponse

router = APIRouter()


@router.get("", response_model=list[LotResponse])
async def get_lots(
    lot_service: LotServiceDep,
    auction_id: uuid.UUID = Query(...),
):
    return await lot_service.get_by_auction_id(auction_id)


@router.post("", response_model=LotResponse)
async def create_lot(
    data: LotCreateRequest,
    user: CurrentUser,
    lot_service: LotServiceDep,
):
    return await lot_service.create(data, user)


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
    user: CurrentUser,
    lot_service: LotServiceDep,
):
    return await lot_service.update(lot_id, data, user)


@router.delete("/{lot_id}")
async def delete_lot(
    lot_id: uuid.UUID,
    user: CurrentUser,
    lot_service: LotServiceDep,
):
    await lot_service.delete(lot_id, user)
    return {"detail": "Lot deleted successfully"}
