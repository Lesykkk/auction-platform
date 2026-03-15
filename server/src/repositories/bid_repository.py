import uuid
from models.bid import Bid


class BidRepository:
    def __init__(self):
        self._storage: dict[uuid.UUID, Bid] = {}

    async def get(self, bid_id: uuid.UUID) -> Bid | None:
        return self._storage.get(bid_id)

    async def get_all(self) -> list[Bid]:
        return list(self._storage.values())

    async def get_by_lot_id(self, lot_id: uuid.UUID) -> list[Bid]:
        return [
            bid for bid in self._storage.values()
            if bid.lot_id == lot_id
        ]

    async def create(self, bid: Bid) -> Bid:
        self._storage[bid.id] = bid
        return bid

    async def update(self, bid: Bid) -> Bid:
        self._storage[bid.id] = bid
        return bid

    async def delete(self, bid_id: uuid.UUID) -> None:
        self._storage.pop(bid_id, None)
