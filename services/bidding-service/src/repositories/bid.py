import uuid
from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

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

    async def find_all_by_user_id(
        self,
        user_id: uuid.UUID,
        filters: BaseFilterParams,
        pagination: PaginationParams,
    ) -> tuple[Sequence[Bid], int]:
        query = select(self.model).where(self.model.user_id == user_id)
        query = self._apply_filters(query, filters)
        return await self._get_paginated(query, pagination)

    async def get_highest_bids_for_lot_ids(self, lot_ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, Bid]:
        if not lot_ids:
            return {}

        ranked_bids = (
            select(
                self.model.id.label("id"),
                self.model.lot_id.label("lot_id"),
                func.row_number()
                .over(partition_by=self.model.lot_id, order_by=(self.model.amount.desc(), self.model.created_at.desc()))
                .label("row_number"),
            )
            .where(self.model.lot_id.in_(lot_ids))
            .subquery()
        )

        highest_bid_ids_query: Select = select(ranked_bids.c.id, ranked_bids.c.lot_id).where(ranked_bids.c.row_number == 1)
        highest_bid_ids = await self.db.execute(highest_bid_ids_query)
        id_to_lot = {row.id: row.lot_id for row in highest_bid_ids}
        if not id_to_lot:
            return {}

        bids = await self.db.execute(select(self.model).where(self.model.id.in_(list(id_to_lot.keys()))))
        return {id_to_lot[bid.id]: bid for bid in bids.scalars().all()}

    async def find_lot_ids_by_user_id(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        result = await self.db.execute(
            select(self.model.lot_id).where(self.model.user_id == user_id).distinct()
        )
        return list(result.scalars().all())
