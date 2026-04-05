from fastapi import APIRouter

from controllers.auction_controller import router as auction_controller
from controllers.lot_controller import router as lot_controller
from controllers.internal_controller import router as internal_controller

router = APIRouter()

router.include_router(auction_controller, prefix="/auctions", tags=["Auctions"])
router.include_router(lot_controller, prefix="/lots", tags=["Lots"])
router.include_router(internal_controller, prefix="/internal", tags=["Internal"])
