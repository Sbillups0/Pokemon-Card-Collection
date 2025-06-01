"""run mass user generation script

Revision ID: 87ac8689a9c0
Revises: c795284cbece
Create Date: 2025-06-01 15:57:55.472735

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from src.api import auth
from src.api.populate_users import generate_a_bajillion_users
from src import database as db


# revision identifiers, used by Alembic.
revision: str = '87ac8689a9c0'
down_revision: Union[str, None] = 'c795284cbece'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    try:
        generate_a_bajillion_users()
    except Exception as e:
        raise Exception(f"Mass user generation failed: {e}")
    pass


def downgrade() -> None:
    """Downgrade schema."""

    #WILL CLEAR EVERY TABLE EXCEPT CARDS AND PACKS
    with db.engine.begin() as connection:
        connection.execute(sa.text("DELETE FROM users"))
        connection.execute(sa.text("DELETE FROM collection"))
        connection.execute(sa.text("DELETE FROM decks"))
        connection.execute(sa.text("DELETE FROM deck_cards"))
        connection.execute(sa.text("DELETE FROM inventory"))
        connection.execute(sa.text("DELETE FROM display"))
