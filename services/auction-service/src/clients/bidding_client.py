import httpx
import uuid
from typing import Any

from core.config import get_settings
from exceptions.handlers import ServiceUnavailableError

settings = get_settings()


class BiddingServiceClient:
    def __init__(self):
        self.base_url = settings.BIDDING_SERVICE_URL

    async def get_winning_bid(self, lot_id: uuid.UUID) -> dict[str, Any] | None:
        """Call bidding-service to get the highest bid for a lot."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/v1/internal/bids/winning?lot_id={lot_id}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                response.raise_for_status()
            except httpx.RequestError as e:
                raise ServiceUnavailableError(detail=f"Bidding service unavailable: {e}")
            return None

    async def settle_lot(self, lot_id: uuid.UUID, seller_id: uuid.UUID) -> None:
        """Call bidding-service to perform financial settlement when a lot closes."""
        async with httpx.AsyncClient() as client:
            try:
                # We tell bidding service that the lot closed, it handles payments & user balance updates
                response = await client.post(
                    f"{self.base_url}/api/v1/internal/payments/settle",
                    json={"lot_id": str(lot_id), "seller_id": str(seller_id)}
                )
                response.raise_for_status()
            except httpx.RequestError as e:
                raise ServiceUnavailableError(detail=f"Bidding service unavailable: {e}")
