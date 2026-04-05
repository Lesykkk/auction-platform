import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.bid import Bid
from repositories.base import SQLAlchemyRepository
from schemas.base import BaseFilterParams, PaginationParams


class BidRepository(SQLAlchemyRepository[Bid, BaseFilterParams]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Bid)

    async def find_all_by_lot_id(
        self,
        lot_id: uuid.UUID,
        filters: BaseFilterParams,
        pagination: PaginationParams,
    ) -> tuple[Sequence[Bid], int]:
        query = select(self.model).where(self.model.lot_id == lot_id)
        query = self._apply_filters(query, filters)
        return await self._get_paginated(query, pagination)

    async def get_highest_bid(self, lot_id: uuid.UUID) -> Bid | None:
        query = (
            select(self.model)
            .where(self.model.lot_id == lot_id)
            .order_by(self.model.amount.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_highest_bid(
        self, lot_id: uuid.UUID, user_id: uuid.UUID
    ) -> Bid | None:
        query = (
            select(self.model)
            .where(self.model.lot_id == lot_id, self.model.user_id == user_id)
            .order_by(self.model.amount.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
