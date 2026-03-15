from models.payment import Payment
from models.user import User
from repositories.payment_repository import PaymentRepository


class PaymentService:
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    async def get_user_payments(self, user: User) -> list[Payment]:
        return await self.payment_repository.get_by_user_id(user.id)
