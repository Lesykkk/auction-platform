import uuid
from models.bid import Bid
from repositories.base_repository import InMemoryRepository


class BidRepository(InMemoryRepository[Bid]):
    async def get_by_lot_id(self, lot_id: uuid.UUID) -> list[Bid]:
        return [
            bid for bid in self._storage.values()
            if bid.lot_id == lot_id
        ]
