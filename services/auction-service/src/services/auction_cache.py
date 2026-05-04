import uuid

from redis.asyncio import Redis
from redis.exceptions import RedisError

from schemas.auction import AuctionResponse


class AuctionCache:
    def __init__(self, redis: Redis, ttl_seconds: int):
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    async def get(self, auction_id: uuid.UUID) -> AuctionResponse | None:
        try:
            cached = await self.redis.get(self._key(auction_id))
        except RedisError:
            return None

        if not cached:
            return None

        try:
            return AuctionResponse.model_validate_json(cached)
        except ValueError:
            await self.invalidate(auction_id)
            return None

    async def set(self, auction: AuctionResponse) -> None:
        try:
            await self.redis.set(
                self._key(auction.id),
                auction.model_dump_json(),
                ex=self.ttl_seconds,
            )
        except RedisError:
            return None

    async def invalidate(self, auction_id: uuid.UUID) -> None:
        try:
            await self.redis.delete(self._key(auction_id))
        except RedisError:
            return None

    def _key(self, auction_id: uuid.UUID) -> str:
        return f"auction:{auction_id}"
