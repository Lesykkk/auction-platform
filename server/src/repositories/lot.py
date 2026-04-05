import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.lot import Lot
from repositories.base import SQLAlchemyRepository
from schemas.lot import LotFilterParams
from schemas.base import PaginationParams


class LotRepository(SQLAlchemyRepository[Lot, LotFilterParams]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Lot)

    async def find_all_by_auction_id(
        self,
        auction_id: uuid.UUID,
        filters: LotFilterParams,
        pagination: PaginationParams,
    ) -> tuple[Sequence[Lot], int]:
        query = select(self.model).where(self.model.auction_id == auction_id)
        query = self._apply_filters(query, filters)
        return await self._get_paginated(query, pagination)

    async def find_lots_by_auction_id(self, auction_id: uuid.UUID) -> Sequence[Lot]:
        query = select(self.model).where(self.model.auction_id == auction_id)
        result = await self.db.execute(query)
        return result.scalars().all()
