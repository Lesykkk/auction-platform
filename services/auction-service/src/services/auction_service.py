import uuid
from typing import Sequence

from exceptions.handlers import NotFoundError, ForbiddenError, BusinessLogicError
from models.auction import Auction, AuctionStatus
from models.lot import LotStatus
from repositories.auction import AuctionRepository
from repositories.lot import LotRepository
from schemas.auction import AuctionCreateRequest, AuctionUpdateRequest, AuctionFilterParams
from schemas.base import PaginationParams
from clients.bidding_client import BiddingServiceClient


class AuctionService:
    def __init__(
        self,
        auction_repository: AuctionRepository,
        lot_repository: LotRepository,
        bidding_client: BiddingServiceClient,
    ):
        self.auction_repository = auction_repository
        self.lot_repository = lot_repository
        self.bidding_client = bidding_client

    async def get_all(
        self,
        filters: AuctionFilterParams,
        pagination: PaginationParams,
    ) -> tuple[Sequence[Auction], int]:
        return await self.auction_repository.find_all(filters=filters, pagination=pagination)

    async def get_by_id(self, auction_id: uuid.UUID) -> Auction:
        auction = await self.auction_repository.find_by_id(auction_id)
        if not auction:
            raise NotFoundError("Auction not found")
        return auction

    async def create(self, data: AuctionCreateRequest, user_id: uuid.UUID) -> Auction:
        auction = Auction(
            title=data.title,
            description=data.description,
            user_id=user_id,
            closes_at=data.closes_at,
        )
        return await self.auction_repository.save(auction)

    async def update(
        self, auction_id: uuid.UUID, data: AuctionUpdateRequest, user_id: uuid.UUID,
    ) -> Auction:
        auction = await self.get_by_id(auction_id)
        if str(auction.user_id) != str(user_id):
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

    async def delete(self, auction_id: uuid.UUID, user_id: uuid.UUID) -> None:
        auction = await self.get_by_id(auction_id)
        if str(auction.user_id) != str(user_id):
            raise ForbiddenError("Only the organizer can delete this auction")
        if auction.status != AuctionStatus.PENDING:
            raise BusinessLogicError("Only PENDING auctions can be deleted")

        lots = await self.lot_repository.find_lots_by_auction_id(auction_id)
        for lot in lots:
            await self.lot_repository.delete(lot.id)

        await self.auction_repository.delete(auction_id)

    async def open(self, auction_id: uuid.UUID, user_id: uuid.UUID) -> Auction:
        auction = await self.get_by_id(auction_id)
        if str(auction.user_id) != str(user_id):
            raise ForbiddenError("Only auction creator can open the auction")
        if auction.status != AuctionStatus.PENDING:
            raise BusinessLogicError("Only PENDING auctions can be opened")

        auction.status = AuctionStatus.ACTIVE
        await self.auction_repository.save(auction)

        lots = await self.lot_repository.find_lots_by_auction_id(auction_id)
        for lot in lots:
            if lot.status == LotStatus.PENDING:
                lot.status = LotStatus.ACTIVE
                await self.lot_repository.save(lot)

        return auction

    async def close(self, auction_id: uuid.UUID, user_id: uuid.UUID) -> Auction:
        auction = await self.get_by_id(auction_id)
        if str(auction.user_id) != str(user_id):
            raise ForbiddenError("Only auction creator can close the auction")
        if auction.status != AuctionStatus.ACTIVE:
            raise BusinessLogicError("Only ACTIVE auctions can be closed")

        auction.status = AuctionStatus.CLOSED
        await self.auction_repository.save(auction)

        lots = await self.lot_repository.find_lots_by_auction_id(auction_id)
        for lot in lots:
            if lot.status != LotStatus.ACTIVE:
                continue

            # Inter-service call to bidding service
            winning_bid = await self.bidding_client.get_winning_bid(lot.id)
            
            if not winning_bid:
                lot.status = LotStatus.UNSOLD
                await self.lot_repository.save(lot)
                continue

            lot.status = LotStatus.SOLD
            # parse UUID string if necessary
            winner_id_str = winning_bid.get("user_id")
            if winner_id_str:
                 lot.winner_id = uuid.UUID(winner_id_str)
            await self.lot_repository.save(lot)

            # Let bidding service handle all settlements (updates user balances & creates payments)
            await self.bidding_client.settle_lot(lot.id, auction.user_id)

        return auction
