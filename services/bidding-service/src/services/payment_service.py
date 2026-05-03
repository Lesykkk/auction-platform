import uuid
from decimal import Decimal
from typing import Sequence

from sqlalchemy.exc import IntegrityError

from clients.user_client import UserServiceClient
from models.payment import Payment, PaymentStatus
from repositories.bid import BidRepository
from repositories.payment import PaymentRepository
from schemas.base import PaginationParams, BaseFilterParams
from schemas.payment import PaymentFilterParams


class PaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        bid_repository: BidRepository,
        user_client: UserServiceClient,
    ):
        self.payment_repository = payment_repository
        self.bid_repository = bid_repository
        self.user_client = user_client

    async def get_by_user_id(
        self, user_id: uuid.UUID, filters: PaymentFilterParams, pagination: PaginationParams
    ) -> tuple[Sequence[Payment], int]:
        return await self.payment_repository.find_all_by_user_id(user_id, filters, pagination)

    async def settle_lot(self, lot_id: uuid.UUID, seller_id: uuid.UUID) -> None:
        """
        Called by auction-service when a lot is closed.
        Retrieves the winning bid, processes winner's payment and balance.
        Losers are refunded real-time during bidding, so no additional refund logic needed here.
        """
        existing_payment = await self.payment_repository.find_by_lot_id(lot_id)
        if existing_payment:
            return

        winning_bid = await self.bid_repository.get_highest_bid(lot_id)
        if not winning_bid:
            return  # No bids placed

        winner_id = winning_bid.user_id
        winning_amount = winning_bid.amount

        # 1. Process Winner Payment
        payment = Payment(
            lot_id=lot_id,
            user_id=winner_id,
            amount=winning_amount,
            status=PaymentStatus.COMPLETED,
        )
        try:
            await self.payment_repository.save(payment)
        except IntegrityError:
            await self.payment_repository.db.rollback()
            return

        winner_adjusted = False
        seller_adjusted = False

        try:
            # 2. Financial adjustments via User Service
            # A) Deduct winner's funds (already locked)
            await self.user_client.adjust_balance(
                user_id=winner_id,
                delta_balance=-winning_amount,
                delta_locked=-winning_amount
            )
            winner_adjusted = True

            # B) Transfer funds to seller
            await self.user_client.adjust_balance(
                user_id=seller_id,
                delta_balance=winning_amount,
                delta_locked=Decimal("0.0")
            )
            seller_adjusted = True
        except Exception:
            if seller_adjusted:
                try:
                    await self.user_client.adjust_balance(
                        user_id=seller_id,
                        delta_balance=-winning_amount,
                        delta_locked=Decimal("0.0"),
                    )
                except Exception:
                    pass

            if winner_adjusted:
                try:
                    await self.user_client.adjust_balance(
                        user_id=winner_id,
                        delta_balance=winning_amount,
                        delta_locked=winning_amount,
                    )
                except Exception:
                    pass

            await self.payment_repository.delete(payment.id)
            raise
