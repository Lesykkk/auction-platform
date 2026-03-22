import uuid
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from models.base import UUIDInMemoryMixin

ModelType = TypeVar("ModelType", bound=UUIDInMemoryMixin)

class AbstractRepository(ABC, Generic[ModelType]):
    @abstractmethod
    async def find_by_id(self, id: uuid.UUID) -> ModelType | None:
        pass

    @abstractmethod
    async def find_all(self) -> list[ModelType]:
        pass

    @abstractmethod
    async def save(self, entity: ModelType) -> ModelType:
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> None:
        pass


class InMemoryRepository(AbstractRepository[ModelType]):
    def __init__(self):
        self._storage: dict[uuid.UUID, ModelType] = {}

    async def find_by_id(self, id: uuid.UUID) -> ModelType | None:
        return self._storage.get(id)

    async def find_all(self) -> list[ModelType]:
        return list(self._storage.values())

    async def save(self, entity: ModelType) -> ModelType:
        self._storage[entity.id] = entity
        return entity

    async def delete(self, id: uuid.UUID) -> None:
        self._storage.pop(id, None)
