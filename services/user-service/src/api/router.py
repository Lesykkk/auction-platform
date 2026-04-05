from fastapi import APIRouter

from controllers.auth_controller import router as auth_controller
from controllers.user_controller import router as user_controller
from controllers.internal_controller import router as internal_controller

router = APIRouter()

router.include_router(auth_controller, prefix="/auth", tags=["Auth"])
router.include_router(user_controller, prefix="/users", tags=["Users"])
router.include_router(internal_controller, prefix="/internal", tags=["Internal"])
