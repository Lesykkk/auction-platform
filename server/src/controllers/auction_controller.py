import uuid
from fastapi import APIRouter

from api.dependencies import CurrentUser, AuctionServiceDep
from schemas.auction import AuctionCreateRequest, AuctionUpdateRequest, AuctionResponse

router = APIRouter()


@router.get("", response_model=list[AuctionResponse])
async def get_auctions(
    auction_service: AuctionServiceDep,
):
    return await auction_service.get_all()


@router.get("/{auction_id}", response_model=AuctionResponse)
async def get_auction(
    auction_id: uuid.UUID,
    auction_service: AuctionServiceDep,
):
    return await auction_service.get_by_id(auction_id)


@router.post("", response_model=AuctionResponse)
async def create_auction(
    data: AuctionCreateRequest,
    user: CurrentUser,
    auction_service: AuctionServiceDep,
):
    return await auction_service.create(data, user)


@router.patch("/{auction_id}", response_model=AuctionResponse)
async def update_auction(
    auction_id: uuid.UUID,
    data: AuctionUpdateRequest,
    user: CurrentUser,
    auction_service: AuctionServiceDep,
):
    return await auction_service.update(auction_id, data, user)


@router.delete("/{auction_id}")
async def delete_auction(
    auction_id: uuid.UUID,
    user: CurrentUser,
    auction_service: AuctionServiceDep,
):
    await auction_service.delete(auction_id, user)
    return {"detail": "Auction deleted successfully"}


@router.post("/{auction_id}/open", response_model=AuctionResponse)
async def open_auction(
    auction_id: uuid.UUID,
    user: CurrentUser,
    auction_service: AuctionServiceDep,
):
    return await auction_service.open(auction_id, user)


@router.post("/{auction_id}/close", response_model=AuctionResponse)
async def close_auction(
    auction_id: uuid.UUID,
    user: CurrentUser,
    auction_service: AuctionServiceDep,
):
    return await auction_service.close(auction_id, user)
