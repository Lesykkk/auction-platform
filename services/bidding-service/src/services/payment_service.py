import uuid
from decimal import Decimal
from typing import Sequence

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
        Retrieves all highest bids per user for this lot, processes winner
        and refunds others. Updates balances via user-service.
        """
        winning_bid = await self.bid_repository.get_highest_bid(lot_id)
        if not winning_bid:
            return  # No bids placed

        winner_id = winning_bid.user_id
        winning_amount = winning_bid.amount

        # Find ALL bids for this lot to figure out who else needs a refund
        # We process each user only once (their highest bid on this lot)
        lots_bids, _ = await self.bid_repository.find_all_by_lot_id(
            lot_id, BaseFilterParams(), PaginationParams(page=1, limit=10000)
        )

        processed_users = set()

        for bid in lots_bids:
            uid = bid.user_id
            if uid in processed_users:
                continue
            
            # get their highest
            # (Note: if find_all_by_lot_id orders by amount desc, the first we see is their max.
            # But let's just make a specific query to be safe)
            user_max_bid = await self.bid_repository.get_user_highest_bid(lot_id, uid)
            if not user_max_bid:
                continue

            processed_users.add(uid)
            locked_amount = user_max_bid.amount

            if uid == winner_id:
                # 1. Winner logic
                payment = Payment(
                    lot_id=lot_id,
                    user_id=winner_id,
                    amount=winning_amount,
                    status=PaymentStatus.COMPLETED,
                )
                await self.payment_repository.save(payment)

                # Deduct from balance AND locked_balance for the winner
                await self.user_client.adjust_balance(
                    user_id=winner_id,
                    delta_balance=-winning_amount,
                    delta_locked=-locked_amount
                )

                # Transfer funds to seller (they get the balance, but it's not locked)
                await self.user_client.adjust_balance(
                    user_id=seller_id,
                    delta_balance=winning_amount,
                    delta_locked=Decimal("0.0")
                )
            else:
                # 2. Loser refund logic
                payment = Payment(
                    lot_id=lot_id,
                    user_id=uid,
                    amount=locked_amount,
                    status=PaymentStatus.REFUNDED,
                )
                await self.payment_repository.save(payment)

                # Unblock their funds
                await self.user_client.adjust_balance(
                    user_id=uid,
                    delta_balance=Decimal("0.0"),
                    delta_locked=-locked_amount
                )
