import uuid
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from schemas.base import PaginationParams

ModelType = TypeVar("ModelType")
FilterType = TypeVar("FilterType")


class AbstractRepository(ABC, Generic[ModelType, FilterType]):
    @abstractmethod
    async def find_by_id(self, id: uuid.UUID) -> ModelType | None:
        pass

    @abstractmethod
    async def find_all(
        self,
        filters: FilterType,
        pagination: PaginationParams
    ) -> tuple[list[ModelType], int]:
        pass

    @abstractmethod
    async def save(self, entity: ModelType) -> ModelType:
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> None:
        pass
