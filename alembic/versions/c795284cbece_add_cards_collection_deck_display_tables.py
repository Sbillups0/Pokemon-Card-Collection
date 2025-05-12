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
    pass



def downgrade() -> None:
    pass
