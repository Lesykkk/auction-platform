from fastapi import APIRouter

from api.dependencies import CurrentUser, PaymentServiceDep
from schemas.payment import PaymentResponse

router = APIRouter()


@router.get("", response_model=list[PaymentResponse])
async def get_payments(
    user: CurrentUser,
    payment_service: PaymentServiceDep,
):
    return await payment_service.get_user_payments(user)
