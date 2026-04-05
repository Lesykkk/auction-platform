import uuid
from decimal import Decimal
from typing import Sequence

from exceptions.handlers import NotFoundError, ForbiddenError, BusinessLogicError
from models.auction import AuctionStatus
from models.lot import Lot, LotStatus
from repositories.auction import AuctionRepository
from repositories.lot import LotRepository
from schemas.base import PaginationParams
from schemas.lot import LotCreateRequest, LotUpdateRequest, LotFilterParams


class LotService:
    def __init__(
        self,
        lot_repository: LotRepository,
        auction_repository: AuctionRepository,
    ):
        self.lot_repository = lot_repository
        self.auction_repository = auction_repository

    async def get_by_id(self, lot_id: uuid.UUID) -> Lot:
        lot = await self.lot_repository.find_by_id(lot_id)
        if not lot:
            raise NotFoundError("Lot not found")
        return lot

    async def get_by_auction_id(
        self,
        auction_id: uuid.UUID,
        filters: LotFilterParams,
        pagination: PaginationParams,
    ) -> tuple[Sequence[Lot], int]:
        return await self.lot_repository.find_all_by_auction_id(auction_id, filters, pagination)

    async def create(self, data: LotCreateRequest, organizer_id: uuid.UUID) -> Lot:
        auction = await self.auction_repository.find_by_id(data.auction_id)
        if not auction:
            raise NotFoundError("Auction not found")
        if str(auction.user_id) != str(organizer_id):
            raise ForbiddenError("Only the auction organizer can add lots")
        if auction.status != AuctionStatus.PENDING:
            raise BusinessLogicError("Lots can only be added to PENDING auctions")
        if data.starting_price <= Decimal("0.0"):
            raise BusinessLogicError("Starting price must be positive")
        if data.min_bid_increment <= Decimal("0.0"):
            raise BusinessLogicError("Min bid increment must be positive")

        lot = Lot(**data.model_dump())
        lot.current_price = data.starting_price
        return await self.lot_repository.save(lot)

    async def update(self, lot_id: uuid.UUID, data: LotUpdateRequest, organizer_id: uuid.UUID) -> Lot:
        lot = await self.get_by_id(lot_id)
        auction = await self.auction_repository.find_by_id(lot.auction_id)
        if not auction:
            raise NotFoundError("Auction not found")
        if str(auction.user_id) != str(organizer_id):
            raise ForbiddenError("Only the organizer can update this lot")
        if lot.status != LotStatus.PENDING:
            raise BusinessLogicError("Only PENDING lots can be updated")

        if data.title is not None:
            lot.title = data.title
        if data.description is not None:
            lot.description = data.description
        if data.starting_price is not None:
            if data.starting_price <= Decimal("0.0"):
                raise BusinessLogicError("Starting price must be positive")
            lot.starting_price = data.starting_price
        if data.min_bid_increment is not None:
            if data.min_bid_increment <= Decimal("0.0"):
                raise BusinessLogicError("Min bid increment must be positive")
            lot.min_bid_increment = data.min_bid_increment

        return await self.lot_repository.save(lot)

    async def delete(self, lot_id: uuid.UUID, organizer_id: uuid.UUID) -> None:
        lot = await self.get_by_id(lot_id)
        auction = await self.auction_repository.find_by_id(lot.auction_id)
        if not auction:
            raise NotFoundError("Auction not found")
        if str(auction.user_id) != str(organizer_id):
            raise ForbiddenError("Only the organizer can delete this lot")
        if lot.status != LotStatus.PENDING:
            raise BusinessLogicError("Only PENDING lots can be deleted")

        await self.lot_repository.delete(lot_id)
