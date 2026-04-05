"""
Internal endpoints.
"""
import uuid
from fastapi import APIRouter, Depends

from api.dependencies import DbDep, get_payment_service, PaymentServiceDep
from repositories.bid import BidRepository
from schemas.bid import BidResponse
from schemas.payment import SettleLotRequest

router = APIRouter()


@router.get("/bids/winning", response_model=BidResponse)
async def get_winning_bid_internal(lot_id: uuid.UUID, db: DbDep):
    """Used by auction-service during lot close to fetch highest bid."""
    repo = BidRepository(db)
    from exceptions.handlers import NotFoundError
    bid = await repo.get_highest_bid(lot_id)
    if not bid:
        raise NotFoundError("No bids found for lot")
    return bid


@router.post("/payments/settle")
async def settle_lot_internal(data: SettleLotRequest, payment_service: PaymentServiceDep):
    """Used by auction-service to trigger financial settlement for a closed lot."""
    await payment_service.settle_lot(data.lot_id, data.seller_id)
    return {"detail": "Lot settled successfully"}
