import uuid
from typing import TypeVar, Generic

from models.base import UUIDInMemoryMixin
from schemas.base import PaginationParams, BaseFilterParams
from repositories.base import AbstractRepository

InMemoryModelType = TypeVar("InMemoryModelType", bound=UUIDInMemoryMixin)
InMemoryFilterType = TypeVar("InMemoryFilterType", bound=BaseFilterParams)


class InMemoryRepository(
    AbstractRepository[InMemoryModelType, InMemoryFilterType],
    Generic[InMemoryModelType, InMemoryFilterType]
):
    def __init__(self):
        self._storage: dict[uuid.UUID, InMemoryModelType] = {}

    async def find_by_id(self, id: uuid.UUID) -> InMemoryModelType | None:
        return self._storage.get(id)

    async def find_all(
        self, 
        filters: InMemoryFilterType,
        pagination: PaginationParams
    ) -> tuple[list[InMemoryModelType], int]:
        items = list(self._storage.values())
        items = self._apply_filters(items, filters)
        total = len(items)
        return items[pagination.offset : pagination.offset + pagination.limit], total

    async def save(self, entity: InMemoryModelType) -> InMemoryModelType:
        self._storage[entity.id] = entity
        return entity

    async def delete(self, id: uuid.UUID) -> None:
        self._storage.pop(id, None)

    def _apply_filters(self, items: list[InMemoryModelType], filters: InMemoryFilterType) -> list[InMemoryModelType]:
        for key, value in filters.model_dump(exclude_none=True).items():
            items = [item for item in items if getattr(item, key) == value]
        return items
