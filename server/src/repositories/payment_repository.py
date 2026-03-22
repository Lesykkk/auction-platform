import uuid
from models.payment import Payment
from repositories.base_repository import InMemoryRepository


class PaymentRepository(InMemoryRepository[Payment]):
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Payment]:
        return [
            payment for payment in self._storage.values()
            if payment.user_id == user_id
        ]
