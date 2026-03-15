import uuid
from models.user import User


class UserRepository:
    def __init__(self):
        self._storage: dict[uuid.UUID, User] = {}

    async def get(self, user_id: uuid.UUID) -> User | None:
        return self._storage.get(user_id)

    async def get_all(self) -> list[User]:
        return list(self._storage.values())

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

    async def create(self, user: User) -> User:
        self._storage[user.id] = user
        return user

    async def update(self, user: User) -> User:
        self._storage[user.id] = user
        return user

    async def delete(self, user_id: uuid.UUID) -> None:
        self._storage.pop(user_id, None)
