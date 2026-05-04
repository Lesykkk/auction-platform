"""
Internal endpoints for auction-service.
"""
import uuid
from fastapi import APIRouter

from api.dependencies import DbDep
from repositories.lot import LotRepository
from repositories.auction import AuctionRepository
from schemas.lot import LotResponse, LotPriceUpdateRequest
from schemas.auction import AuctionResponse
from schemas.base import UUIDListRequest
from services.lot_service import LotService

router = APIRouter()


@router.get("/health")
async def healthcheck():
    return {"status": "ok", "service": "auction-service"}


@router.post("/batch/lots", response_model=list[LotResponse])
async def get_lots_internal_batch(data: UUIDListRequest, db: DbDep):
    repo = LotRepository(db)
    lots = await repo.find_by_ids(data.ids)
    return list(lots)


@router.post("/batch/auctions", response_model=list[AuctionResponse])
async def get_auctions_internal_batch(data: UUIDListRequest, db: DbDep):
    repo = AuctionRepository(db)
    auctions = await repo.find_by_ids(data.ids)
    return list(auctions)


@router.get("/lots/{lot_id}", response_model=LotResponse)
async def get_lot_internal(lot_id: uuid.UUID, db: DbDep):
    """Used by bidding-service when placing a bid to ensure lot is ACTIVE."""
    repo = LotRepository(db)
    from exceptions.handlers import NotFoundError
    lot = await repo.find_by_id(lot_id)
    if not lot:
         raise NotFoundError("Lot not found")
    return lot

@router.patch("/lots/{lot_id}/current-price", response_model=LotResponse)
async def update_lot_price_internal(
    lot_id: uuid.UUID, 
    data: LotPriceUpdateRequest, 
    db: DbDep
):
    """Used by bidding-service to update lot price after a new valid bid."""
    service = LotService(LotRepository(db), AuctionRepository(db))
    return await service.update_current_price(lot_id, data.current_price)

@router.get("/auctions/{auction_id}", response_model=AuctionResponse)
async def get_auction_internal(auction_id: uuid.UUID, db: DbDep):
    """Used by bidding-service to ensure bidder is not the auction organizer."""
    repo = AuctionRepository(db)
    from exceptions.handlers import NotFoundError
    auction = await repo.find_by_id(auction_id)
    if not auction:
         raise NotFoundError("Auction not found")
    return auction
