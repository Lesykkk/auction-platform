import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.auction import Auction
from repositories.base import SQLAlchemyRepository
from schemas.auction import AuctionFilterParams
from schemas.base import PaginationParams


class AuctionRepository(SQLAlchemyRepository[Auction, AuctionFilterParams]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Auction)

    async def find_auctions_by_user_id(self, user_id: uuid.UUID) -> Sequence[Auction]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()
