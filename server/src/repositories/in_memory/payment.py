import uuid

from models.payment import Payment
from repositories.in_memory.base import InMemoryRepository
from schemas.base import PaginationParams
from schemas.payment import PaymentFilterParams


class PaymentRepository(InMemoryRepository[Payment, PaymentFilterParams]):
    async def find_all_by_user_id(
        self,
        user_id: uuid.UUID,
        filters: PaymentFilterParams,
        pagination: PaginationParams,
    ) -> tuple[list[Payment], int]:
        items = [item for item in self._storage.values() if item.user_id == user_id]
        items = self._apply_filters(items, filters)
        total = len(items)
        return items[pagination.offset : pagination.offset + pagination.limit], total