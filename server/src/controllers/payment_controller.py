from fastapi import APIRouter, Depends

from api.dependencies import get_current_user, get_payment_service
from models.user import User
from schemas.payment import PaymentResponse
from services.payment_service import PaymentService

router = APIRouter()


@router.get("", response_model=list[PaymentResponse])
async def get_payments(
    user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
):
    return await payment_service.get_user_payments(user)
