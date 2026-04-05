from models.payment import Payment
from models.user import User
from repositories.in_memory.payment import PaymentRepository
from schemas.base import PaginationParams
from schemas.payment import PaymentFilterParams


class PaymentService:
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    async def get_user_payments(
        self,
        user: User,
        filters: PaymentFilterParams,
        pagination: PaginationParams,
    ) -> tuple[list[Payment], int]:
        return await self.payment_repository.find_all_by_user_id(user.id, filters, pagination)
