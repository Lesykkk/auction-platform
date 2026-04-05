from models.auction import Auction
from repositories.in_memory.base import InMemoryRepository
from schemas.auction import AuctionFilterParams


class AuctionRepository(InMemoryRepository[Auction, AuctionFilterParams]):
    pass
