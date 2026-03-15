from fastapi import APIRouter

from controllers.auth_controller import router as auth_controller
from controllers.user_controller import router as user_controller
from controllers.lot_controller import router as lot_controller
from controllers.auction_controller import router as auction_controller
from controllers.bid_controller import router as bid_controller
from controllers.payment_controller import router as payment_controller

router = APIRouter()

router.include_router(auth_controller, prefix="/auth", tags=["Auth"])
router.include_router(user_controller, prefix="/users", tags=["Users"])
router.include_router(auction_controller, prefix="/auctions", tags=["Auctions"])
router.include_router(bid_controller, prefix="/bids", tags=["Bids"])
router.include_router(payment_controller, prefix="/payments", tags=["Payments"])
