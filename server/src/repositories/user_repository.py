from models.user import User
from repositories.base_repository import InMemoryRepository


class UserRepository(InMemoryRepository[User]):
    async def get_by_username(self, username: str) -> User | None:
        for user in self._storage.values():
            if user.username == username:
                return user
        return None

    async def get_by_email(self, email: str) -> User | None:
        for user in self._storage.values():
            if user.email == email:
                return user
        return None
