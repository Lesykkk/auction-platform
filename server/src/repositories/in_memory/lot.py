import uuid

from models.lot import Lot
from repositories.in_memory.base import InMemoryRepository
from schemas.base import PaginationParams
from schemas.lot import LotFilterParams


class LotRepository(InMemoryRepository[Lot, LotFilterParams]):
    async def find_all_by_auction_id(
        self,
        auction_id: uuid.UUID,
        filters: LotFilterParams,
        pagination: PaginationParams,
    ) -> tuple[list[Lot], int]:
        items = [item for item in self._storage.values() if item.auction_id == auction_id]
        items = self._apply_filters(items, filters)
        total = len(items)
        return items[pagination.offset : pagination.offset + pagination.limit], total

    async def find_lots_by_auction_id(self, auction_id: uuid.UUID) -> list[Lot]:
        """Unpaginated — for internal business logic (open/close/delete auction)."""
        return [item for item in self._storage.values() if item.auction_id == auction_id]
