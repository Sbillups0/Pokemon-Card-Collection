"""Add cards, collection, deck, display tables

Revision ID: c795284cbece
Revises: b825c97e31ba
Create Date: 2025-05-07 23:09:26.986697

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c795284cbece'
down_revision: Union[str, None] = 'b825c97e31ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- cards table ----    # ---- deck table ----
    op.create_table(
        "deck",
        sa.Column("id", sa.Integer, sa.Identity(always=True, start=1), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("card_id", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_deck_user", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"], name="fk_deck_card", ondelete="CASCADE")
    )

    # ---- display table ----
    op.create_table(
        "display",
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("card_id", sa.Integer, primary_key=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_display_user", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"], name="fk_display_card", ondelete="CASCADE")
    )



def downgrade() -> None:
    op.drop_table("display")
    op.drop_table("deck")
    op.drop_table("collection")
    op.drop_table("cards")
