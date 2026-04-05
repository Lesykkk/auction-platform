import uuid
from decimal import Decimal
from typing import Sequence

from exceptions.handlers import NotFoundError, BusinessLogicError, ForbiddenError
from clients.user_client import UserServiceClient
from clients.auction_client import AuctionServiceClient
from models.bid import Bid
from repositories.bid import BidRepository
from schemas.base import BaseFilterParams, PaginationParams
from schemas.bid import BidCreateRequest


class BidService:
    def __init__(
        self,
        bid_repository: BidRepository,
        user_client: UserServiceClient,
        auction_client: AuctionServiceClient,
    ):
        self.bid_repository = bid_repository
        self.user_client = user_client
        self.auction_client = auction_client

    async def get_by_lot_id(
        self, lot_id: uuid.UUID, filters: BaseFilterParams, pagination: PaginationParams
    ) -> tuple[Sequence[Bid], int]:
        return await self.bid_repository.find_all_by_lot_id(lot_id, filters, pagination)

    async def get_highest_bid(self, lot_id: uuid.UUID) -> Bid | None:
        return await self.bid_repository.get_highest_bid(lot_id)

    async def place_bid(self, data: BidCreateRequest, user_id: uuid.UUID) -> Bid:
        # 1. Fetch cross-service data
        user = await self.user_client.get_user(user_id)
        if not user:
            raise NotFoundError("User not found")

        lot = await self.auction_client.get_lot(data.lot_id)
        if not lot:
            raise NotFoundError("Lot not found")

        auction_id = uuid.UUID(lot["auction_id"])
        auction = await self.auction_client.get_auction(auction_id)
        if not auction:
            raise NotFoundError("Auction not found")

        # 2. Extract values and validate
        lot_status = lot["status"]
        current_price = Decimal(lot["current_price"])
        min_increment = Decimal(lot["min_bid_increment"])
        auction_user_id = uuid.UUID(auction["user_id"])
        
        balance = Decimal(user["balance"])
        locked_balance = Decimal(user["locked_balance"])
        available_balance = balance - locked_balance

        if lot_status != "ACTIVE":
            raise BusinessLogicError("Can only bid on ACTIVE lots")

        if auction_user_id == user_id:
            raise ForbiddenError("Auction organizer cannot bid on their own lots")

        if data.amount < current_price + min_increment:
            raise BusinessLogicError("Bid amount too low")

        # Check existing bid by this user to calculate if they can afford this new bid
        previous_bid = await self.bid_repository.get_user_highest_bid(data.lot_id, user_id)
        previous_bid_amount = previous_bid.amount if previous_bid else Decimal("0.0")

        # How much MORE they need to lock
        required_additional_funds = data.amount - previous_bid_amount

        if available_balance < required_additional_funds:
            raise BusinessLogicError("Insufficient available funds")

        # 3. Create Bid
        bid = Bid(
            lot_id=data.lot_id,
            user_id=user_id,
            amount=data.amount,
        )
        saved_bid = await self.bid_repository.save(bid)

        # 4. Adjust locked balance in User Service
        # We increase their locked balance by the additional amount they are bidding
        await self.user_client.adjust_balance(
            user_id=user_id,
            delta_balance=Decimal("0.0"),
            delta_locked=required_additional_funds
        )

        return saved_bid
