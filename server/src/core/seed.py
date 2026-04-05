import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from core.database import async_session_maker
from core.security import hash_password

# SQL Repositories
from repositories.user import UserRepository
from repositories.lot import LotRepository
from repositories.auction import AuctionRepository
from repositories.bid import BidRepository

from models.user import User
from models.lot import Lot, LotStatus
from models.auction import Auction, AuctionStatus
from models.bid import Bid

logger = logging.getLogger(__name__)


async def seed_data():
    async with async_session_maker() as db:
        try:
            user_repo = UserRepository(db)
            lot_repo = LotRepository(db)
            auction_repo = AuctionRepository(db)
            bid_repo = BidRepository(db)
            
            existing_user = await user_repo.find_by_username("testbuyer")
            if existing_user:
                logger.info("Seed data already exists")
                return

            # Create users
            testbuyer = User(
                username="testbuyer",
                email="testbuyer@example.com",
                hashed_password=hash_password("testbuyer"),
                balance=Decimal("10000.0"),
            )
            testbuyer = await user_repo.save(testbuyer)

            testseller = User(
                username="testseller",
                email="testseller@example.com",
                hashed_password=hash_password("testseller"),
                balance=Decimal("500.0"),
            )
            testseller = await user_repo.save(testseller)

            # 1. Create Auction 1 (testseller)
            auction1 = Auction(
                title="Spring Art Collection",
                description="Exclusive paintings and sculptures.",
                user_id=testseller.id,
                status=AuctionStatus.PENDING,
                closes_at=datetime.now(timezone.utc) + timedelta(days=3),
            )
            auction1 = await auction_repo.save(auction1)

            # Lots for Auction 1
            lot1 = Lot(
                auction_id=auction1.id,
                title="Vintage Rolex Submariner",
                description="A beautiful vintage watch from 1980 in excellent condition.",
                starting_price=Decimal("5000.0"),
                min_bid_increment=Decimal("100.0"),
                current_price=Decimal("5000.0"),
                status=LotStatus.PENDING,
            )
            await lot_repo.save(lot1)

            lot2 = Lot(
                auction_id=auction1.id,
                title="1st Edition Charizard Holographic",
                description="PSA 10 Gem Mint Pokemon Card. Extremely rare.",
                starting_price=Decimal("10000.0"),
                min_bid_increment=Decimal("500.0"),
                current_price=Decimal("10000.0"),
                status=LotStatus.PENDING,
            )
            await lot_repo.save(lot2)

            # Open Auction 1 (This also sets lot1 and lot2 to ACTIVE)
            auction1.status = AuctionStatus.ACTIVE
            lot1.status = LotStatus.ACTIVE
            lot2.status = LotStatus.ACTIVE
            
            await auction_repo.save(auction1)
            await lot_repo.save(lot1)
            await lot_repo.save(lot2)

            # 2. Create Auction 2 (testbuyer)
            auction2 = Auction(
                title="Tech Gadgets Liquidation",
                description="Brand new electronics.",
                user_id=testbuyer.id,
                status=AuctionStatus.PENDING,
                closes_at=datetime.now(timezone.utc) + timedelta(days=7),
            )
            auction2 = await auction_repo.save(auction2)

            lot3 = Lot(
                auction_id=auction2.id,
                title="MacBook Pro M3 Max",
                description="Brand new, unopened, 128GB RAM, 4TB SSD.",
                starting_price=Decimal("4500.0"),
                min_bid_increment=Decimal("50.0"),
                current_price=Decimal("4500.0"),
                status=LotStatus.PENDING,
            )
            await lot_repo.save(lot3)
            
            # 3. Add initial bids for Lot 1
            bid1 = Bid(
                lot_id=lot1.id,
                user_id=testbuyer.id,
                amount=Decimal("5200.0"),
            )
            await bid_repo.save(bid1)
            
            # Update Lot 1 current price and Buyer's locked balance
            lot1.current_price = bid1.amount
            await lot_repo.save(lot1)
            
            testbuyer.locked_balance += bid1.amount
            await user_repo.save(testbuyer)

            await db.commit()
            logger.info("Seed data created successfully! You can login with testbuyer:testbuyer and testseller:testseller")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to seed database: {e}")
            raise
