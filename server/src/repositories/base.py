import uuid
from typing import TypeVar, Generic, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.base import PaginationParams, BaseFilterParams

from models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
FilterType = TypeVar("FilterType", bound=BaseFilterParams)


class SQLAlchemyRepository(Generic[ModelType, FilterType]):
    def __init__(self, db: AsyncSession, model: type[ModelType]):
        self.db = db
        self.model = model

    async def find_by_id(self, id: uuid.UUID) -> ModelType | None:
        return await self.db.get(self.model, id)

    async def find_all(
        self,
        filters: FilterType,
        pagination: PaginationParams,
    ) -> tuple[Sequence[ModelType], int]:
        query = select(self.model)
        query = self._apply_filters(query, filters)
        return await self._get_paginated(query, pagination)

    async def save(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, id: uuid.UUID) -> None:
        entity = await self.find_by_id(id)
        if entity:
            await self.db.delete(entity)

    def _apply_filters(self, query, filters: FilterType):
        for key, value in filters.model_dump(exclude_none=True).items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        return query

    async def _get_paginated(
        self,
        query,
        pagination: PaginationParams,
    ) -> tuple[Sequence[ModelType], int]:
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        query = query.order_by(self.model.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self.db.execute(query)
        items = result.scalars().all()
        return items, total
