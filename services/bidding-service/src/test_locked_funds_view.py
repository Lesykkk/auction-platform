import asyncio
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient

os.environ.setdefault("POSTGRES_USER", "admin")
os.environ.setdefault("POSTGRES_PASSWORD", "admin")
os.environ.setdefault("POSTGRES_DB", "auction_bidding")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5435")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from api import dependencies as bid_dependencies
from main import app
from schemas.base import PaginationParams
from schemas.bid import MyBidResponse, MyBidsSummary
from services.bid_service import BidService


class FakeBidRepository:
    def __init__(self, bids, highest_by_lot, all_lot_ids):
        self._bids = bids
        self._highest_by_lot = highest_by_lot
        self._all_lot_ids = all_lot_ids

    async def find_all_by_user_id(self, user_id, filters, pagination):
        user_bids = [bid for bid in self._bids if bid.user_id == user_id]
        start = pagination.offset
        end = start + pagination.limit
        return user_bids[start:end], len(user_bids)

    async def find_lot_ids_by_user_id(self, user_id):
        return self._all_lot_ids

    async def get_highest_bids_for_lot_ids(self, lot_ids):
        return {lot_id: bid for lot_id, bid in self._highest_by_lot.items() if lot_id in lot_ids}


class FakeAuctionClient:
    def __init__(self, lots, auctions):
        self._lots = lots
        self._auctions = auctions

    async def get_lots_batch(self, lot_ids):
        requested = {str(lot_id) for lot_id in lot_ids}
        return [lot for lot in self._lots if lot["id"] in requested]

    async def get_auctions_batch(self, auction_ids):
        requested = {str(auction_id) for auction_id in auction_ids}
        return [auction for auction in self._auctions if auction["id"] in requested]


def _make_bid(bid_id, lot_id, user_id, amount, created_at):
    return SimpleNamespace(
        id=bid_id,
        lot_id=lot_id,
        user_id=user_id,
        amount=Decimal(amount),
        created_at=created_at,
    )


def test_bid_service_marks_only_current_leading_bid_as_locked():
    user_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    lot_one_id = uuid.uuid4()
    lot_two_id = uuid.uuid4()
    auction_one_id = uuid.uuid4()
    auction_two_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    older_bid = _make_bid(uuid.uuid4(), lot_one_id, user_id, "150.00", now)
    current_locked_bid = _make_bid(uuid.uuid4(), lot_one_id, user_id, "220.00", now)
    outbid_bid = _make_bid(uuid.uuid4(), lot_two_id, user_id, "180.00", now)
    competing_highest = _make_bid(uuid.uuid4(), lot_two_id, other_user_id, "250.00", now)

    repository = FakeBidRepository(
        bids=[current_locked_bid, outbid_bid, older_bid],
        highest_by_lot={
            lot_one_id: current_locked_bid,
            lot_two_id: competing_highest,
        },
        all_lot_ids=[lot_one_id, lot_two_id],
    )
    auction_client = FakeAuctionClient(
        lots=[
            {
                "id": str(lot_one_id),
                "auction_id": str(auction_one_id),
                "title": "Lot One",
                "status": "ACTIVE",
                "current_price": "220.00",
            },
            {
                "id": str(lot_two_id),
                "auction_id": str(auction_two_id),
                "title": "Lot Two",
                "status": "ACTIVE",
                "current_price": "250.00",
            },
        ],
        auctions=[
            {"id": str(auction_one_id), "title": "Auction One", "status": "ACTIVE"},
            {"id": str(auction_two_id), "title": "Auction Two", "status": "ACTIVE"},
        ],
    )
    service = BidService(repository, user_client=None, auction_client=auction_client)

    items, total, summary = asyncio.run(
        service.get_by_user_id(user_id, SimpleNamespace(model_dump=lambda exclude_none=True: {}), PaginationParams(page=1, limit=20))
    )

    assert total == 3
    by_id = {item.id: item for item in items}
    assert by_id[current_locked_bid.id].is_locked is True
    assert by_id[current_locked_bid.id].locked_amount == Decimal("220.00")
    assert by_id[older_bid.id].is_locked is False
    assert by_id[older_bid.id].locked_amount == Decimal("0.0")
    assert by_id[outbid_bid.id].is_locked is False
    assert summary.total_locked_amount == Decimal("220.00")


def test_get_my_bids_requires_authentication():
    client = TestClient(app)
    response = client.get("/api/v1/bids/me")
    assert response.status_code == 401


def test_get_my_bids_returns_paginated_enriched_response():
    user_id = uuid.uuid4()

    class FakeBidService:
        async def get_by_user_id(self, current_user_id, filters, pagination):
            assert current_user_id == user_id
            assert pagination.page == 1
            assert pagination.limit == 20
            return (
                [
                    MyBidResponse(
                        id=uuid.uuid4(),
                        lot_id=uuid.uuid4(),
                        auction_id=uuid.uuid4(),
                        user_id=user_id,
                        amount=Decimal("150.00"),
                        current_price=Decimal("150.00"),
                        lot_title="Lot",
                        lot_status="ACTIVE",
                        auction_title="Auction",
                        auction_status="ACTIVE",
                        is_locked=True,
                        locked_amount=Decimal("150.00"),
                        created_at=datetime.now(timezone.utc),
                    )
                ],
                1,
                MyBidsSummary(total_locked_amount=Decimal("150.00")),
            )

    app.dependency_overrides[bid_dependencies.get_current_user_id] = lambda: user_id
    app.dependency_overrides[bid_dependencies.get_bid_service] = lambda: FakeBidService()
    try:
        client = TestClient(app)
        response = client.get("/api/v1/bids/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["total"] == 1
    assert payload["summary"]["total_locked_amount"] == "150.00"
    assert payload["items"][0]["is_locked"] is True
