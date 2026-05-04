"""add unique payment per lot

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    exists = bind.execute(
        sa.text(
            """
            select 1
            from pg_constraint
            where conname = 'uq_payments_lot_id'
            """
        )
    ).scalar()
    if not exists:
        op.create_unique_constraint("uq_payments_lot_id", "payments", ["lot_id"])


def downgrade() -> None:
    bind = op.get_bind()
    exists = bind.execute(
        sa.text(
            """
            select 1
            from pg_constraint
            where conname = 'uq_payments_lot_id'
            """
        )
    ).scalar()
    if exists:
        op.drop_constraint("uq_payments_lot_id", "payments", type_="unique")
