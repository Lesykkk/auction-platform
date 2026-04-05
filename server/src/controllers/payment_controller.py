from fastapi import APIRouter, Depends

from api.dependencies import CurrentUser, PaymentServiceDep, PaginationParamsDep, PaymentFilterParamsDep
from schemas.payment import PaymentResponse
from schemas.base import PaginatedResponse, Meta

router = APIRouter()


@router.get("", response_model=PaginatedResponse[PaymentResponse])
async def get_payments(
    user: CurrentUser,
    payment_service: PaymentServiceDep,
    pagination: PaginationParamsDep,
    filters: PaymentFilterParamsDep,
):
    items, total = await payment_service.get_user_payments(user, filters, pagination)
    return PaginatedResponse(
        items=items,
        meta=Meta(total=total, page=pagination.page, limit=pagination.limit),
    )
