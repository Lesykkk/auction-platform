from models.auction import Auction
from repositories.base_repository import InMemoryRepository


class AuctionRepository(InMemoryRepository[Auction]):
    pass
