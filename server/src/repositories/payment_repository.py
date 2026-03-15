import uuid
from models.payment import Payment


class PaymentRepository:
    def __init__(self):
        self._storage: dict[uuid.UUID, Payment] = {}

    async def get(self, payment_id: uuid.UUID) -> Payment | None:
        return self._storage.get(payment_id)

    async def get_all(self) -> list[Payment]:
        return list(self._storage.values())

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Payment]:
        return [
            payment for payment in self._storage.values()
            if payment.user_id == user_id
        ]

    async def create(self, payment: Payment) -> Payment:
        self._storage[payment.id] = payment
        return payment

    async def update(self, payment: Payment) -> Payment:
        self._storage[payment.id] = payment
        return payment

    async def delete(self, payment_id: uuid.UUID) -> None:
        self._storage.pop(payment_id, None)
