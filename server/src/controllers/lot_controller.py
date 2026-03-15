from fastapi import APIRouter, Depends

from api.dependencies import get_current_user, get_lot_service
from models.user import User
from schemas.lot import LotCreateRequest, LotUpdateRequest, LotResponse
from services.lot_service import LotService

router = APIRouter()


@router.get("", response_model=list[LotResponse])
async def get_lots(
    lot_service: LotService = Depends(get_lot_service),
):
    return await lot_service.get_all()


@router.get("/{lot_id}", response_model=LotResponse)
async def get_lot(
    lot_id: str,
    lot_service: LotService = Depends(get_lot_service),
):
    return await lot_service.get_by_id(lot_id)


@router.post("", response_model=LotResponse)
async def create_lot(
    data: LotCreateRequest,
    user: User = Depends(get_current_user),
    lot_service: LotService = Depends(get_lot_service),
):
    return await lot_service.create(data, user)


@router.patch("/{lot_id}", response_model=LotResponse)
async def update_lot(
    lot_id: str,
    data: LotUpdateRequest,
    user: User = Depends(get_current_user),
    lot_service: LotService = Depends(get_lot_service),
):
    return await lot_service.update(lot_id, data, user)


@router.delete("/{lot_id}")
async def delete_lot(
    lot_id: str,
    user: User = Depends(get_current_user),
    lot_service: LotService = Depends(get_lot_service),
):
    await lot_service.delete(lot_id, user)
    return {"detail": "Lot deleted successfully"}
