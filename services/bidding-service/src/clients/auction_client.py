import httpx
import uuid
from typing import Any

from core.config import get_settings
from exceptions.handlers import ServiceUnavailableError

settings = get_settings()


class AuctionServiceClient:
    def __init__(self):
        self.base_url = settings.AUCTION_SERVICE_URL

    async def get_lot(self, lot_id: uuid.UUID) -> dict[str, Any] | None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/internal/lots/{lot_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                response.raise_for_status()
            except httpx.RequestError as e:
                raise ServiceUnavailableError(detail=f"Auction service unavailable: {e}")
            return None

    async def get_auction(self, auction_id: uuid.UUID) -> dict[str, Any] | None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/internal/auctions/{auction_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                response.raise_for_status()
            except httpx.RequestError as e:
                raise ServiceUnavailableError(detail=f"Auction service unavailable: {e}")
            return None
