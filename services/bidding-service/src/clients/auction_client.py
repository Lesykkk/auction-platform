import httpx
import uuid
from decimal import Decimal
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

    async def update_lot_price(self, lot_id: uuid.UUID, amount: Decimal) -> None:
        """Internal: tell auction-service that the lot has a new current_price."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(
                    f"{self.base_url}/api/v1/internal/lots/{lot_id}/current-price",
                    json={"current_price": str(amount)}
                )
                response.raise_for_status()
            except httpx.RequestError as e:
                raise ServiceUnavailableError(detail=f"Auction service unavailable: {e}")

    async def get_lots_batch(self, lot_ids: list[uuid.UUID]) -> list[dict[str, Any]]:
        if not lot_ids:
            return []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/internal/batch/lots",
                    json={"ids": [str(lot_id) for lot_id in lot_ids]},
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise ServiceUnavailableError(detail=f"Auction service unavailable: {e}")

    async def get_auctions_batch(self, auction_ids: list[uuid.UUID]) -> list[dict[str, Any]]:
        if not auction_ids:
            return []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/internal/batch/auctions",
                    json={"ids": [str(auction_id) for auction_id in auction_ids]},
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise ServiceUnavailableError(detail=f"Auction service unavailable: {e}")
