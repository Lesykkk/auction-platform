"""
Internal endpoints for auction-service.
"""
import uuid
from fastapi import APIRouter

from api.dependencies import DbDep
from repositories.lot import LotRepository
from repositories.auction import AuctionRepository
from schemas.lot import LotResponse
from schemas.auction import AuctionResponse

router = APIRouter()

@router.get("/lots/{lot_id}", response_model=LotResponse)
async def get_lot_internal(lot_id: uuid.UUID, db: DbDep):
    """Used by bidding-service when placing a bid to ensure lot is ACTIVE."""
    repo = LotRepository(db)
    from exceptions.handlers import NotFoundError
    lot = await repo.find_by_id(lot_id)
    if not lot:
         raise NotFoundError("Lot not found")
    return lot

@router.get("/auctions/{auction_id}", response_model=AuctionResponse)
async def get_auction_internal(auction_id: uuid.UUID, db: DbDep):
    """Used by bidding-service to ensure bidder is not the auction organizer."""
    repo = AuctionRepository(db)
    from exceptions.handlers import NotFoundError
    auction = await repo.find_by_id(auction_id)
    if not auction:
         raise NotFoundError("Auction not found")
    return auction
