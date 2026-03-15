import uuid
from models.lot import Lot


class LotRepository:
    def __init__(self):
        self._storage: dict[uuid.UUID, Lot] = {}

    async def get(self, lot_id: uuid.UUID) -> Lot | None:
        return self._storage.get(lot_id)

    async def get_all(self) -> list[Lot]:
        return list(self._storage.values())

    async def get_by_auction_id(self, auction_id: uuid.UUID) -> list[Lot]:
        return [lot for lot in self._storage.values() if lot.auction_id == auction_id]

    async def create(self, lot: Lot) -> Lot:
        self._storage[lot.id] = lot
        return lot

    async def update(self, lot: Lot) -> Lot:
        self._storage[lot.id] = lot
        return lot

    async def delete(self, lot_id: uuid.UUID) -> None:
        self._storage.pop(lot_id, None)
