import uuid
from typing import Annotated, AsyncGenerator
from fastapi import Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_maker
from core.security import decode_token
from exceptions.handlers import UnauthorizedError

from repositories.bid import BidRepository
from repositories.payment import PaymentRepository
from clients.user_client import UserServiceClient
from clients.auction_client import AuctionServiceClient
from services.bid_service import BidService
from services.payment_service import PaymentService
from schemas.base import PaginationParams
from schemas.payment import PaymentFilterParams


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


DbDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_bid_repository(db: DbDep) -> BidRepository:
    return BidRepository(db)


def get_payment_repository(db: DbDep) -> PaymentRepository:
    return PaymentRepository(db)


def get_user_client() -> UserServiceClient:
    return UserServiceClient()


def get_auction_client() -> AuctionServiceClient:
    return AuctionServiceClient()


def get_bid_service(
    bid_repo: BidRepository = Depends(get_bid_repository),
    user_client: UserServiceClient = Depends(get_user_client),
    auction_client: AuctionServiceClient = Depends(get_auction_client),
) -> BidService:
    return BidService(bid_repo, user_client, auction_client)


def get_payment_service(
    payment_repo: PaymentRepository = Depends(get_payment_repository),
    bid_repo: BidRepository = Depends(get_bid_repository),
    user_client: UserServiceClient = Depends(get_user_client),
) -> PaymentService:
    return PaymentService(payment_repo, bid_repo, user_client)


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
BidServiceDep = Annotated[BidService, Depends(get_bid_service)]
PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]
PaymentFilterParamsDep = Annotated[PaymentFilterParams, Depends()]
