import uuid
from models.bid import Bid
from models.lot import LotStatus
from models.user import User
from repositories.auction_repository import AuctionRepository
from repositories.bid_repository import BidRepository
from repositories.lot_repository import LotRepository
from repositories.user_repository import UserRepository
from schemas.bid import BidCreateRequest
from exceptions.handlers import (
    NotFoundError,
    ForbiddenError,
    BusinessLogicError,
)


class BidService:
    def __init__(
        self,
        bid_repository: BidRepository,
        auction_repository: AuctionRepository,
        lot_repository: LotRepository,
        user_repository: UserRepository,
    ):
        self.bid_repository = bid_repository
        self.auction_repository = auction_repository
        self.lot_repository = lot_repository
        self.user_repository = user_repository

    async def place_bid(self, data: BidCreateRequest, user: User) -> Bid:
        lot = await self.lot_repository.find_by_id(data.lot_id)
        if not lot:
            raise NotFoundError("Lot not found")

        if lot.status != LotStatus.ACTIVE:
            raise BusinessLogicError("Lot is not active")

        auction = await self.auction_repository.find_by_id(lot.auction_id)
        if not auction:
            raise NotFoundError("Auction not found")

        if auction.user_id == user.id:
            raise ForbiddenError("Organizer cannot bid on their own auction's lots")

        if data.amount <= lot.current_price:
            raise BusinessLogicError(
                f"Bid must be greater than current price ({lot.current_price})"
            )

        min_required = lot.current_price + lot.min_bid_increment
        if data.amount < min_required:
            raise BusinessLogicError(
                f"Bid must be at least {min_required} "
                f"(current price + minimum increment)"
            )

        available_balance = user.balance - user.locked_balance
        if data.amount > available_balance:
            raise BusinessLogicError("Insufficient available balance")

        # Unlock previous bid from this user on this specific lot (if any)
        existing_bids = await self.bid_repository.get_by_lot_id(data.lot_id)
        user_previous_bids = [b for b in existing_bids if b.user_id == user.id]
        if user_previous_bids:
            previous_highest = max(user_previous_bids, key=lambda b: b.amount)
            user.locked_balance -= previous_highest.amount

        # Lock new bid amount
        user.locked_balance += data.amount
        await self.user_repository.save(user)

        # Update lot current price
        lot.current_price = data.amount
        await self.lot_repository.save(lot)

        bid = Bid(
            lot_id=data.lot_id,
            user_id=user.id,
            amount=data.amount,
        )
        return await self.bid_repository.save(bid)

    async def get_bids_by_lot(self, lot_id: uuid.UUID) -> list[Bid]:
        lot = await self.lot_repository.find_by_id(lot_id)
        if not lot:
            raise NotFoundError("Lot not found")

        return await self.bid_repository.get_by_lot_id(lot_id)
