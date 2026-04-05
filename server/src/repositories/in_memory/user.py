from models.user import User
from repositories.in_memory.base import InMemoryRepository
from schemas.user import UserFilterParams


class UserRepository(InMemoryRepository[User, UserFilterParams]):
    async def find_by_username(self, username: str) -> User | None:
        return next(
            (u for u in self._storage.values() if u.username == username),
            None,
        )

    async def find_by_email(self, email: str) -> User | None:
        return next(
            (u for u in self._storage.values() if u.email == email),
            None,
        )
