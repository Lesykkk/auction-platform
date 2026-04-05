import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from repositories.base import SQLAlchemyRepository
from schemas.user import UserFilterParams


class UserRepository(SQLAlchemyRepository[User, UserFilterParams]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def find_by_username(self, username: str) -> User | None:
        query = select(self.model).where(self.model.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        query = select(self.model).where(self.model.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
