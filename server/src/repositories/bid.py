import uuid
from typing import Sequence
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.bid import Bid
from repositories.base import SQLAlchemyRepository
from schemas.bid import BidFilterParams
from schemas.base import PaginationParams


class BidRepository(SQLAlchemyRepository[Bid, BidFilterParams]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Bid)

    async def find_all_by_lot_id(
        self,
        lot_id: uuid.UUID,
        filters: BidFilterParams,
        pagination: PaginationParams,
    ) -> tuple[Sequence[Bid], int]:
        query = select(self.model).where(self.model.lot_id == lot_id)
        query = self._apply_filters(query, filters)
        return await self._get_paginated(query, pagination)

    async def find_bids_by_lot_id(self, lot_id: uuid.UUID) -> Sequence[Bid]:
        query = select(self.model).where(self.model.lot_id == lot_id).order_by(desc(self.model.amount))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_winning_bid_by_lot_id(self, lot_id: uuid.UUID) -> Bid | None:
        query = (
            select(self.model)
            .where(self.model.lot_id == lot_id)
            .order_by(desc(self.model.amount))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
