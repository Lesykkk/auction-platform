from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.security import decode_token
from exceptions.handlers import UnauthorizedError
from models.user import User
from repositories.user_repository import UserRepository
from repositories.lot_repository import LotRepository
from repositories.auction_repository import AuctionRepository
from repositories.bid_repository import BidRepository
from repositories.payment_repository import PaymentRepository
from services.auth_service import AuthService
from services.user_service import UserService
from services.lot_service import LotService
from services.auction_service import AuctionService
from services.bid_service import BidService
from services.payment_service import PaymentService

user_repository = UserRepository()
lot_repository = LotRepository()
auction_repository = AuctionRepository()
bid_repository = BidRepository()
payment_repository = PaymentRepository()

security = HTTPBearer()


def get_user_repository() -> UserRepository:
    return user_repository


def get_lot_repository() -> LotRepository:
    return lot_repository


def get_auction_repository() -> AuctionRepository:
    return auction_repository


def get_bid_repository() -> BidRepository:
    return bid_repository


def get_payment_repository() -> PaymentRepository:
    return payment_repository


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)


def get_lot_service(
    lot_repo: LotRepository = Depends(get_lot_repository),
    auction_repo: AuctionRepository = Depends(get_auction_repository),
) -> LotService:
    return LotService(lot_repo, auction_repo)


def get_auction_service(
    auction_repo: AuctionRepository = Depends(get_auction_repository),
    lot_repo: LotRepository = Depends(get_lot_repository),
    bid_repo: BidRepository = Depends(get_bid_repository),
    payment_repo: PaymentRepository = Depends(get_payment_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuctionService:
    return AuctionService(
        auction_repo, lot_repo, bid_repo, payment_repo, user_repo,
    )


def get_bid_service(
    bid_repo: BidRepository = Depends(get_bid_repository),
    auction_repo: AuctionRepository = Depends(get_auction_repository),
    lot_repo: LotRepository = Depends(get_lot_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> BidService:
    return BidService(bid_repo, auction_repo, lot_repo, user_repo)


def get_payment_service(
    payment_repo: PaymentRepository = Depends(get_payment_repository),
) -> PaymentService:
    return PaymentService(payment_repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    payload = decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    import uuid
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Invalid token payload")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Invalid user ID format in token")

    user = await user_repo.get(user_id)
    if not user:
        raise UnauthorizedError("User not found")

    return user
