"""create global inventory

Revision ID: e91d0c24f7d0
Revises:
Create Date: 2025-03-30 11:23:36.782933

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic. 
revision: str = "e91d0c24f7d0"
down_revision: Union[str, None] = "9b4118923246"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "packs",
        sa.Column("id", sa.Integer, sa.Identity(always=True, start=1), autoincrement=True, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("price", sa.Integer, nullable=False),
    )
    op.execute(sa.text(
            """
            INSERT INTO packs (name, price) 
            VALUES 
            ('Basic', 25), ('Jungle', 50), ('Fossil', 100), ('Team Rocket', 200)
            """
        )
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, sa.Identity(always=True, start=1), autoincrement=True, primary_key=True),
        sa.Column("username", sa.Text, nullable=False),
        sa.Column("coins", sa.Integer, nullable=False),
        sa.CheckConstraint("coins >= 0", name="check_coins_positive"), # Check constraint to ensure coins are non-negative
    )
    op.create_table(
        "inventory",
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("pack_id", sa.Integer, primary_key=True),
        sa.Column("quantity", sa.Integer, nullable=False),

        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_id", ondelete='CASCADE'), #Foreign Key to Transactions
        sa.ForeignKeyConstraint(["pack_id"], ["packs.id"], name="fk_pack_name", ondelete='cascade'), #Foreign Key to Accounts
    )


def downgrade():
    op.drop_table("packs")
    op.drop_table("users")
    op.drop_table("inventory")

