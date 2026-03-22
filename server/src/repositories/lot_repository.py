import uuid
from models.lot import Lot
from repositories.base_repository import InMemoryRepository


class LotRepository(InMemoryRepository[Lot]):
    async def get_by_auction_id(self, auction_id: uuid.UUID) -> list[Lot]:
        return [lot for lot in self._storage.values() if lot.auction_id == auction_id]
