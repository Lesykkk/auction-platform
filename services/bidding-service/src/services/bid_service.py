import uuid
from decimal import Decimal
from typing import Sequence

from exceptions.handlers import NotFoundError, BusinessLogicError, ForbiddenError
from clients.user_client import UserServiceClient
from clients.auction_client import AuctionServiceClient
from models.bid import Bid
from repositories.bid import BidRepository
from schemas.base import BaseFilterParams, PaginationParams
from schemas.bid import BidCreateRequest, MyBidResponse, MyBidsSummary


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

    async def get_by_user_id(
        self,
        user_id: uuid.UUID,
        filters: BaseFilterParams,
        pagination: PaginationParams,
    ) -> tuple[list[MyBidResponse], int, MyBidsSummary]:
        bids, total = await self.bid_repository.find_all_by_user_id(user_id, filters, pagination)
        all_user_lot_ids = await self.bid_repository.find_lot_ids_by_user_id(user_id)
        global_highest_bids_by_lot = await self.bid_repository.get_highest_bids_for_lot_ids(all_user_lot_ids)
        lot_ids = list({bid.lot_id for bid in bids})

        highest_bids_by_lot = await self.bid_repository.get_highest_bids_for_lot_ids(lot_ids)
        lots = await self.auction_client.get_lots_batch(lot_ids)
        lots_by_id = {uuid.UUID(lot["id"]): lot for lot in lots}

        auction_ids = list({uuid.UUID(lot["auction_id"]) for lot in lots if lot.get("auction_id")})
        auctions = await self.auction_client.get_auctions_batch(auction_ids)
        auctions_by_id = {uuid.UUID(auction["id"]): auction for auction in auctions}

        items: list[MyBidResponse] = []
        total_locked_amount = sum(
            (bid.amount for bid in global_highest_bids_by_lot.values() if bid.user_id == user_id),
            Decimal("0.0"),
        )

        for bid in bids:
            lot = lots_by_id.get(bid.lot_id)
            if not lot:
                raise NotFoundError("Lot not found")

            auction_id = uuid.UUID(lot["auction_id"])
            auction = auctions_by_id.get(auction_id)
            if not auction:
                raise NotFoundError("Auction not found")

            highest_bid = highest_bids_by_lot.get(bid.lot_id)
            is_locked = bool(highest_bid and highest_bid.user_id == user_id and highest_bid.id == bid.id)
            locked_amount = bid.amount if is_locked else Decimal("0.0")

            items.append(
                MyBidResponse(
                    id=bid.id,
                    lot_id=bid.lot_id,
                    auction_id=auction_id,
                    user_id=bid.user_id,
                    amount=bid.amount,
                    current_price=Decimal(lot["current_price"]),
                    lot_title=lot["title"],
                    lot_status=lot["status"],
                    auction_title=auction["title"],
                    auction_status=auction["status"],
                    is_locked=is_locked,
                    locked_amount=locked_amount,
                    created_at=bid.created_at,
                )
            )

        return items, total, MyBidsSummary(total_locked_amount=total_locked_amount)

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

        # 3. Determine how much is currently locked for this lot.
        # Only the current leader's amount is still reserved; older bids may
        # exist in history even after their lock has been released.
        previous_highest = await self.bid_repository.get_highest_bid(data.lot_id)
        currently_locked_for_this_lot = Decimal("0.0")
        if previous_highest and previous_highest.user_id == user_id:
            currently_locked_for_this_lot = previous_highest.amount

        required_additional_funds = data.amount - currently_locked_for_this_lot

        if available_balance < required_additional_funds:
            raise BusinessLogicError("Insufficient available funds")

        # 4. Create and Save Bid
        bid = Bid(
            lot_id=data.lot_id,
            user_id=user_id,
            amount=data.amount,
        )
        saved_bid = await self.bid_repository.save(bid)

        current_bid_locked = False
        previous_leader_unlocked = False

        try:
            # 5. Financial adjustments
            # A) Lock funds for CURRENT bidder
            await self.user_client.adjust_balance(
                user_id=user_id,
                delta_balance=Decimal("0.0"),
                delta_locked=required_additional_funds
            )
            current_bid_locked = True

            # B) Unlock funds for PREVIOUS leader (if different user)
            if previous_highest and previous_highest.user_id != user_id:
                await self.user_client.adjust_balance(
                    user_id=previous_highest.user_id,
                    delta_balance=Decimal("0.0"),
                    delta_locked=-previous_highest.amount
                )
                previous_leader_unlocked = True

            # 6. Update current price in Auction Service
            await self.auction_client.update_lot_price(data.lot_id, data.amount)
            return saved_bid
        except Exception:
            # Best-effort compensation if a later cross-service call fails.
            if previous_leader_unlocked and previous_highest:
                try:
                    await self.user_client.adjust_balance(
                        user_id=previous_highest.user_id,
                        delta_balance=Decimal("0.0"),
                        delta_locked=previous_highest.amount,
                    )
                except Exception:
                    pass

            if current_bid_locked:
                try:
                    await self.user_client.adjust_balance(
                        user_id=user_id,
                        delta_balance=Decimal("0.0"),
                        delta_locked=-required_additional_funds,
                    )
                except Exception:
                    pass

            await self.bid_repository.delete(saved_bid.id)
            raise
