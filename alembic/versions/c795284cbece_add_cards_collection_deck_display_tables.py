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
        "decks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("deck_name", sa.Text, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_id", ondelete="CASCADE"),
    )
    op.create_table(
        "deck_cards",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("deck_id", sa.Integer, nullable=False),
        sa.Column("card_name", sa.Text, nullable=False),
        sa.ForeignKeyConstraint(["deck_id"], ["decks.id"], name="fk_deck_id", ondelete="CASCADE"),
    )



def downgrade() -> None:
    op.drop_table("deck_cards")
    op.drop_table("decks")
    pass
