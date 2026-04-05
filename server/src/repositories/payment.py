import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.payment import Payment
from repositories.base import SQLAlchemyRepository
from schemas.payment import PaymentFilterParams
from schemas.base import PaginationParams


class PaymentRepository(SQLAlchemyRepository[Payment, PaymentFilterParams]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Payment)

    async def find_all_by_user_id(
        self,
        user_id: uuid.UUID,
        filters: PaymentFilterParams,
        pagination: PaginationParams,
    ) -> tuple[Sequence[Payment], int]:
        query = select(self.model).where(self.model.user_id == user_id)
        query = self._apply_filters(query, filters)
        return await self._get_paginated(query, pagination)

    async def find_payments_by_user_id(self, user_id: uuid.UUID) -> Sequence[Payment]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()
