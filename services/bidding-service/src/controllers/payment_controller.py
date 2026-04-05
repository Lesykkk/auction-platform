from fastapi import APIRouter

from api.dependencies import CurrentUserId, PaymentServiceDep, PaginationParamsDep, PaymentFilterParamsDep
from schemas.payment import PaymentResponse
from schemas.base import PaginatedResponse, Meta

router = APIRouter()


@router.get("", response_model=PaginatedResponse[PaymentResponse])
async def get_my_payments(
    user_id: CurrentUserId,
    payment_service: PaymentServiceDep,
    pagination: PaginationParamsDep,
    filters: PaymentFilterParamsDep,
):
    items, total = await payment_service.get_by_user_id(user_id, filters, pagination)
    return PaginatedResponse(
        items=items,
        meta=Meta(total=total, page=pagination.page, limit=pagination.limit),
    )
