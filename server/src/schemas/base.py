import math
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, model_validator


T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class Meta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int = 0

    @model_validator(mode="after")
    def compute_total_pages(self) -> "Meta":
        self.total_pages = math.ceil(self.total / self.limit) if self.limit > 0 else 1
        return self


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: Meta


class BaseFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
