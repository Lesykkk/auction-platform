import uuid

from models.bid import Bid
from repositories.in_memory.base import InMemoryRepository
from schemas.base import PaginationParams
from schemas.bid import BidFilterParams


class BidRepository(InMemoryRepository[Bid, BidFilterParams]):
    async def find_all_by_lot_id(
        self,
        lot_id: uuid.UUID,
        filters: BidFilterParams,
        pagination: PaginationParams,
    ) -> tuple[list[Bid], int]:
        items = [item for item in self._storage.values() if item.lot_id == lot_id]
        items = self._apply_filters(items, filters)
        total = len(items)
        return items[pagination.offset : pagination.offset + pagination.limit], total

    async def find_winning_bid_by_lot_id(self, lot_id: uuid.UUID) -> Bid | None:
        bids = [item for item in self._storage.values() if item.lot_id == lot_id]
        if not bids:
            return None
        return max(bids, key=lambda b: b.amount)

    async def find_bids_by_lot_id(self, lot_id: uuid.UUID) -> list[Bid]:
        """Unpaginated — for internal business logic (close auction refunds, place_bid)."""
        return [item for item in self._storage.values() if item.lot_id == lot_id]