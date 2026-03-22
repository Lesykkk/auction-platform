import uuid
from models.auction import Auction, AuctionStatus
from models.lot import LotStatus
from models.payment import Payment, PaymentStatus
from models.user import User
from repositories.auction_repository import AuctionRepository
from repositories.bid_repository import BidRepository
from repositories.lot_repository import LotRepository
from repositories.payment_repository import PaymentRepository
from repositories.user_repository import UserRepository
from schemas.auction import AuctionCreateRequest, AuctionUpdateRequest
from exceptions.handlers import (
    NotFoundError,
    ForbiddenError,
    BusinessLogicError,
)

class AuctionService:
    def __init__(
        self,
        auction_repository: AuctionRepository,
        lot_repository: LotRepository,
        bid_repository: BidRepository,
        payment_repository: PaymentRepository,
        user_repository: UserRepository,
    ):
        self.auction_repository = auction_repository
        self.lot_repository = lot_repository
        self.bid_repository = bid_repository
        self.payment_repository = payment_repository
        self.user_repository = user_repository

    async def get_all(self) -> list[Auction]:
        return await self.auction_repository.find_all()

    async def get_by_id(self, auction_id: uuid.UUID) -> Auction:
        auction = await self.auction_repository.find_by_id(auction_id)
        if not auction:
            raise NotFoundError("Auction not found")
        return auction

    async def create(
        self, data: AuctionCreateRequest, user: User,
    ) -> Auction:
        auction = Auction(
            title=data.title,
            description=data.description,
            user_id=user.id,
            closes_at=data.closes_at,
        )
        return await self.auction_repository.save(auction)

    async def update(
        self, auction_id: uuid.UUID, data: AuctionUpdateRequest, user: User,
    ) -> Auction:
        auction = await self.get_by_id(auction_id)
        if auction.user_id != user.id:
            raise ForbiddenError("Only auction creator can update the auction")
        if auction.status != AuctionStatus.PENDING:
            raise BusinessLogicError("Only PENDING auctions can be updated")

        if data.title is not None:
            auction.title = data.title
        if data.description is not None:
            auction.description = data.description
        if data.closes_at is not None:
            auction.closes_at = data.closes_at

        return await self.auction_repository.save(auction)

    async def delete(self, auction_id: uuid.UUID, user: User) -> None:
        auction = await self.get_by_id(auction_id)
        if auction.user_id != user.id:
            raise ForbiddenError("Only auction creator can delete the auction")
        if auction.status != AuctionStatus.PENDING:
            raise BusinessLogicError("Only PENDING auctions can be deleted")

        lots = await self.lot_repository.get_by_auction_id(auction_id)
        for lot in lots:
            await self.lot_repository.delete(lot.id)

        await self.auction_repository.delete(auction_id)

    async def open(self, auction_id: uuid.UUID, user: User) -> Auction:
        auction = await self.get_by_id(auction_id)
        if auction.user_id != user.id:
            raise ForbiddenError("Only auction creator can open the auction")
        if auction.status != AuctionStatus.PENDING:
            raise BusinessLogicError("Only PENDING auctions can be opened")

        auction.status = AuctionStatus.ACTIVE
        await self.auction_repository.save(auction)

        lots = await self.lot_repository.get_by_auction_id(auction_id)
        for lot in lots:
            if lot.status == LotStatus.PENDING:
                lot.status = LotStatus.ACTIVE
                await self.lot_repository.save(lot)

        return auction

    async def close(self, auction_id: uuid.UUID, user: User) -> Auction:
        auction = await self.get_by_id(auction_id)
        if auction.user_id != user.id:
            raise ForbiddenError("Only auction creator can close the auction")
        if auction.status != AuctionStatus.ACTIVE:
            raise BusinessLogicError("Only ACTIVE auctions can be closed")

        auction.status = AuctionStatus.CLOSED
        await self.auction_repository.save(auction)

        lots = await self.lot_repository.get_by_auction_id(auction_id)
        for lot in lots:
            if lot.status != LotStatus.ACTIVE:
                continue

            bids = await self.bid_repository.get_by_lot_id(lot.id)
            if not bids:
                lot.status = LotStatus.UNSOLD
                await self.lot_repository.save(lot)
                continue

            # Find the winning bid (highest amount)
            winning_bid = max(bids, key=lambda b: b.amount)

            lot.status = LotStatus.SOLD
            lot.winner_id = winning_bid.user_id
            await self.lot_repository.save(lot)

            # Process winner
            winner = await self.user_repository.find_by_id(winning_bid.user_id)
            if winner:
                winner.balance -= winning_bid.amount
                winner.locked_balance -= winning_bid.amount
                await self.user_repository.save(winner)

                # Credit seller (auction creator)
                seller = await self.user_repository.find_by_id(auction.user_id)
                if seller:
                    seller.balance += winning_bid.amount
                    await self.user_repository.save(seller)

                await self.payment_repository.save(
                    Payment(
                        lot_id=lot.id,
                        user_id=winner.id,
                        amount=winning_bid.amount,
                        status=PaymentStatus.COMPLETED,
                    )
                )

            # Refund other bidders on this lot
            processed_bidders: set[uuid.UUID] = {winning_bid.user_id}
            for bid in sorted(bids, key=lambda b: b.amount, reverse=True):
                if bid.user_id in processed_bidders:
                    continue
                processed_bidders.add(bid.user_id)

                bidder = await self.user_repository.find_by_id(bid.user_id)
                if bidder:
                    bidder_bids = [b for b in bids if b.user_id == bid.user_id]
                    highest_bid = max(bidder_bids, key=lambda b: b.amount)
                    bidder.locked_balance -= highest_bid.amount
                    await self.user_repository.save(bidder)

                    await self.payment_repository.save(
                        Payment(
                            lot_id=lot.id,
                            user_id=bidder.id,
                            amount=highest_bid.amount,
                            status=PaymentStatus.REFUNDED,
                        )
                    )

        return auction
