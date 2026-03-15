import uuid
from models.auction import Auction


class AuctionRepository:
    def __init__(self):
        self._storage: dict[uuid.UUID, Auction] = {}

    async def get(self, auction_id: uuid.UUID) -> Auction | None:
        return self._storage.get(auction_id)

    async def get_all(self) -> list[Auction]:
        return list(self._storage.values())

    async def create(self, auction: Auction) -> Auction:
        self._storage[auction.id] = auction
        return auction

    async def update(self, auction: Auction) -> Auction:
        self._storage[auction.id] = auction
        return auction

    async def delete(self, auction_id: uuid.UUID) -> None:
        self._storage.pop(auction_id, None)
