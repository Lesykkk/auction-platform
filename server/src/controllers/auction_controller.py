import uuid
from fastapi import APIRouter, Depends

from api.dependencies import get_current_user, get_auction_service, get_bid_service, get_lot_service
from models.user import User
from schemas.auction import AuctionCreateRequest, AuctionUpdateRequest, AuctionResponse
from schemas.lot import LotCreateRequest, LotUpdateRequest, LotResponse
from schemas.bid import BidResponse
from services.auction_service import AuctionService
from services.bid_service import BidService
from services.lot_service import LotService

router = APIRouter()


@router.get("", response_model=list[AuctionResponse])
async def get_auctions(
    auction_service: AuctionService = Depends(get_auction_service),
):
    return await auction_service.get_all()


@router.get("/{auction_id}", response_model=AuctionResponse)
async def get_auction(
    auction_id: uuid.UUID,
    auction_service: AuctionService = Depends(get_auction_service),
):
    return await auction_service.get_by_id(auction_id)


@router.post("", response_model=AuctionResponse)
async def create_auction(
    data: AuctionCreateRequest,
    user: User = Depends(get_current_user),
    auction_service: AuctionService = Depends(get_auction_service),
):
    return await auction_service.create(data, user)


@router.patch("/{auction_id}", response_model=AuctionResponse)
async def update_auction(
    auction_id: uuid.UUID,
    data: "AuctionUpdateRequest",
    user: User = Depends(get_current_user),
    auction_service: AuctionService = Depends(get_auction_service),
):
    return await auction_service.update(auction_id, data, user)


@router.delete("/{auction_id}")
async def delete_auction(
    auction_id: uuid.UUID,
    user: User = Depends(get_current_user),
    auction_service: AuctionService = Depends(get_auction_service),
):
    await auction_service.delete(auction_id, user)
    return {"detail": "Auction deleted successfully"}


@router.post("/{auction_id}/open", response_model=AuctionResponse)
async def open_auction(
    auction_id: uuid.UUID,
    user: User = Depends(get_current_user),
    auction_service: AuctionService = Depends(get_auction_service),
):
    return await auction_service.open(auction_id, user)


@router.post("/{auction_id}/close", response_model=AuctionResponse)
async def close_auction(
    auction_id: uuid.UUID,
    user: User = Depends(get_current_user),
    auction_service: AuctionService = Depends(get_auction_service),
):
    return await auction_service.close(auction_id, user)


# Lot Endpoints nested under Auction
@router.get("/{auction_id}/lots", response_model=list[LotResponse])
async def get_auction_lots(
    auction_id: uuid.UUID,
    lot_service: LotService = Depends(get_lot_service),
):
    return await lot_service.get_by_auction_id(auction_id)


@router.post("/{auction_id}/lots", response_model=LotResponse)
async def add_lot_to_auction(
    auction_id: uuid.UUID,
    data: LotCreateRequest,
    user: User = Depends(get_current_user),
    lot_service: LotService = Depends(get_lot_service),
):
    return await lot_service.create(auction_id, data, user)


@router.get("/{auction_id}/lots/{lot_id}", response_model=LotResponse)
async def get_lot(
    auction_id: uuid.UUID,
    lot_id: uuid.UUID,
    lot_service: LotService = Depends(get_lot_service),
):
    # In a real app we might verify lot.auction_id == auction_id
    return await lot_service.get_by_id(lot_id)


@router.patch("/{auction_id}/lots/{lot_id}", response_model=LotResponse)
async def update_lot(
    auction_id: uuid.UUID,
    lot_id: uuid.UUID,
    data: LotUpdateRequest,
    user: User = Depends(get_current_user),
    lot_service: LotService = Depends(get_lot_service),
):
    return await lot_service.update(lot_id, data, user)


@router.delete("/{auction_id}/lots/{lot_id}")
async def delete_lot(
    auction_id: uuid.UUID,
    lot_id: uuid.UUID,
    user: User = Depends(get_current_user),
    lot_service: LotService = Depends(get_lot_service),
):
    await lot_service.delete(lot_id, user)
    return {"detail": "Lot deleted successfully"}


@router.get("/{auction_id}/lots/{lot_id}/bids", response_model=list[BidResponse])
async def get_lot_bids(
    auction_id: uuid.UUID,
    lot_id: uuid.UUID,
    bid_service: BidService = Depends(get_bid_service),
):
    return await bid_service.get_bids_by_lot(lot_id)
