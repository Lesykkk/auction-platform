from fastapi import APIRouter

from controllers.bid_controller import router as bid_controller
from controllers.payment_controller import router as payment_controller
from controllers.internal_controller import router as internal_controller

router = APIRouter()

router.include_router(bid_controller, prefix="/bids", tags=["Bids"])
router.include_router(payment_controller, prefix="/payments", tags=["Payments"])
router.include_router(internal_controller, prefix="/internal", tags=["Internal"])
