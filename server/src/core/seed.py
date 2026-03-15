import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from api.dependencies import user_repository, lot_repository, auction_repository, get_auction_service, get_lot_service
from core.security import hash_password
from models.user import User
from models.lot import Lot, LotStatus
from models.auction import Auction, AuctionStatus

logger = logging.getLogger(__name__)


async def seed_data():
    existing_user = await user_repository.get_by_username("testbuyer")
    if existing_user:
        logger.info("Seed data already exists")
        return

    # Create users
    testbuyer = User(
        username="testbuyer",
        email="testbuyer@example.com",
        hashed_password=hash_password("testbuyer"),
        balance=10000.0,
    )
    testbuyer = await user_repository.create(testbuyer)

    testseller = User(
        username="testseller",
        email="testseller@example.com",
        hashed_password=hash_password("testseller"),
        balance=500.0,
    )
    testseller = await user_repository.create(testseller)

    # 1. Create Auction 1 (testseller)
    auction1 = Auction(
        title="Spring Art Collection",
        description="Exclusive paintings and sculptures.",
        created_by=testseller.id,
        status=AuctionStatus.PENDING,
        closes_at=datetime.now(timezone.utc) + timedelta(days=3),
    )
    auction1 = await auction_repository.create(auction1)

    # Lots for Auction 1
    lot1 = Lot(
        auction_id=auction1.id,
        title="Vintage Rolex Submariner",
        description="A beautiful vintage watch from 1980 in excellent condition.",
        starting_price=5000.0,
        min_bid_increment=100.0,
        status=LotStatus.PENDING,
    )
    await lot_repository.create(lot1)

    lot2 = Lot(
        auction_id=auction1.id,
        title="1st Edition Charizard Holographic",
        description="PSA 10 Gem Mint Pokemon Card. Extremely rare.",
        starting_price=10000.0,
        min_bid_increment=500.0,
        status=LotStatus.PENDING,
    )
    await lot_repository.create(lot2)

    # Open Auction 1 (This also sets lot1 and lot2 to ACTIVE)
    auction1.status = AuctionStatus.ACTIVE
    lot1.status = LotStatus.ACTIVE
    lot2.status = LotStatus.ACTIVE
    
    await auction_repository.update(auction1)
    await lot_repository.update(lot1)
    await lot_repository.update(lot2)

    # 2. Create Auction 2 (testbuyer)
    auction2 = Auction(
        title="Tech Gadgets Liquidation",
        description="Brand new electronics.",
        created_by=testbuyer.id,
        status=AuctionStatus.PENDING,
        closes_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    auction2 = await auction_repository.create(auction2)

    lot3 = Lot(
        auction_id=auction2.id,
        title="MacBook Pro M3 Max",
        description="Brand new, unopened, 128GB RAM, 4TB SSD.",
        starting_price=4500.0,
        min_bid_increment=50.0,
        status=LotStatus.PENDING,
    )
    await lot_repository.create(lot3)

    logger.info("Seed data created successfully! You can login with testbuyer:testbuyer and testseller:testseller")
