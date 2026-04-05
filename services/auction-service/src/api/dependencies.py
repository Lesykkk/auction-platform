import uuid
from typing import Annotated, AsyncGenerator
from fastapi import Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker
from core.security import decode_token
from exceptions.handlers import UnauthorizedError

from repositories.auction import AuctionRepository
from repositories.lot import LotRepository
from services.auction_service import AuctionService
from services.lot_service import LotService
from schemas.base import PaginationParams
from schemas.auction import AuctionFilterParams
from schemas.lot import LotFilterParams
from clients.user_client import UserServiceClient
from clients.bidding_client import BiddingServiceClient


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


DbDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_auction_repository(db: DbDep) -> AuctionRepository:
    return AuctionRepository(db)


def get_lot_repository(db: DbDep) -> LotRepository:
    return LotRepository(db)


def get_user_client() -> UserServiceClient:
    return UserServiceClient()


def get_bidding_client() -> BiddingServiceClient:
    return BiddingServiceClient()


def get_lot_service(
    lot_repo: LotRepository = Depends(get_lot_repository),
    auction_repo: AuctionRepository = Depends(get_auction_repository),
) -> LotService:
    return LotService(lot_repo, auction_repo)


def get_auction_service(
    auction_repo: AuctionRepository = Depends(get_auction_repository),
    lot_repo: LotRepository = Depends(get_lot_repository),
    bidding_client: BiddingServiceClient = Depends(get_bidding_client),
) -> AuctionService:
    return AuctionService(auction_repo, lot_repo, bidding_client)


async def get_current_user_id(request: Request) -> uuid.UUID:
    """Extract user ID from JWT token. Independent validation per service."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid token")
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        raise UnauthorizedError("Invalid token format")

    return user_id


def get_pagination_params(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit)


PaginationParamsDep = Annotated[PaginationParams, Depends(get_pagination_params)]
LotServiceDep = Annotated[LotService, Depends(get_lot_service)]
AuctionServiceDep = Annotated[AuctionService, Depends(get_auction_service)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]
AuctionFilterParamsDep = Annotated[AuctionFilterParams, Depends()]
LotFilterParamsDep = Annotated[LotFilterParams, Depends()]
