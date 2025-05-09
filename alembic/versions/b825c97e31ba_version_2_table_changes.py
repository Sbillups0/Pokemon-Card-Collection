"""version-2-table-changes

Revision ID: b825c97e31ba
Revises: e91d0c24f7d0
Create Date: 2025-05-07 10:52:23.743559

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic. MOST RECENT REVISION
revision: str = 'b825c97e31ba'
down_revision: Union[str, None] = 'e91d0c24f7d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cards",
        sa.Column("id", sa.Integer, sa.Identity(always=True, start=1), autoincrement=True, primary_key=True),
        sa.Column("pack_id", sa.Integer, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("price", sa.Integer, nullable=False),

        sa.ForeignKeyConstraint(["pack_id"], ["packs.id"], name="fk_pack_id", ondelete='CASCADE'), #Foreign Key to Packs
    )
    op.execute(sa.text(
            """
            INSERT INTO cards (pack_id, name, type, price) 
            VALUES 
            (1, 'Pidgy', 'Normal', 10), (1, 'Pidgeotto', 'Normal', 20), (1, 'Pidgeot', 'Normal', 30), (1, 'Sandshrew', 'Ground', 10), (1, 'Sandslash', 'Ground', 20),
            (1, 'Nidoran', 'Poison', 10), (1, 'Nidorina', 'Poison', 20), (1, 'Nidoqueen', 'Poison', 30), (1, 'Vulpix', 'Fire', 30), (1, 'Ninetales', 'Fire', 50),
            (1, 'Igglybuff', 'Normal', 20), (1, 'Jigglypuff', 'Normal', 30), (1, 'Wigglytuff', 'Normal', 50), (1, 'Paras', 'Bug', 20), (1, 'Parasect', 'Bug', 40), 
            (1, 'Slowpoke', 'Water', 20), (1, 'Slowbro', 'Water', 40), (1, 'Doduo', 'Normal', 20), (1, 'Dodrio', 'Normal', 40), (1, 'Gengar VMAX', 'Ghost', 500),
            (2, 'Grimer', 'Poison', 20), (2, 'Muk', 'Poison', 40), (2, 'Ghastly', 'Ghost', 20), (2, 'Haunter', 'Ghost', 40), (2, 'Gengar', 'Ghost', 60),
            (2, 'Onix', 'Rock', 50), (2, 'Steelix', 'Rock', 70), (2, 'Drowzee', 'Psychic', 20), (2, 'Hypno', 'Psychic', 40), (2, 'Krabby', 'Water', 20),
            (2, 'Kingler', 'Water', 40), (2, 'Voltorb', 'Electric', 20), (2, 'Electrode', 'Electric', 40), (2, 'Exeggcute', 'Grass', 20), (2, 'Exeggutor', 'Grass', 40),
            (2, 'Lickitung', 'Normal', 20), (2, 'Lickilicky', 'Normal', 40), (2, 'Tangela', 'Grass', 20), (2, 'Tangrowth', 'Grass', 40), (2, 'Pikachu VMAX', 'Electric', 1000),
            (3, 'Horsea', 'Water', 20), (3, 'Seadra', 'Water', 40), (3, 'Goldeen', 'Water', 20), (3, 'Seaking', 'Water', 40), (3, 'Staryu', 'Water', 20),
            (3, 'Starmie', 'Water', 40), (3, 'Smoochum', 'Ice', 30), (3, 'Jynx', 'Ice', 50), (3, 'Porygon', 'Normal', 20), (3, 'Porygon2', 'Normal', 40),
            (3, 'Porygon-Z', 'Normal', 60), (3, 'Munchlax', 'Normal', 50), (3, 'Snorlax', 'Normal', 100), (3, 'Dratini', 'Dragon', 20), (3, 'Dragonair', 'Dragon', 40), 
            (3, 'Dragonite', 'Dragon', 60), (3, 'Chikorita', 'Grass', 20), (3, 'Bayleef', 'Grass', 40), (3, 'Meganium', 'Grass', 60), (3, 'Umbreon EX', 'Dark', 1500),
            (4, 'Cyndaquil', 'Fire', 20), (4, 'Quilava', 'Fire', 40), (4, 'Typhlosion', 'Fire', 60), (4, 'Rhyhorn', 'Rock', 40), (4, 'Rhydon', 'Rock', 60),
            (4, 'Rhyperior', 'Rock', 80), (4, 'Mareep', 'Electric', 20), (4, 'Flaaffy', 'Electric', 40), (4, 'Ampharos', 'Electric', 60), (4, 'Azurill', 'Water', 20),
            (4, 'Marill', 'Water', 30), (4, 'Azumarill', 'Water', 50), (4, 'Bonsly', 'Rock', 20), (4, 'Sudowoodo', 'Rock', 40), (4, 'Hoppip', 'Grass', 20),
            (4, 'Skiploom', 'Grass', 40), (4, 'Jumpluff', 'Grass', 60), (4, 'Aipom', 'Normal', 20), (4, 'Ambipom', 'Normal', 40), (4, 'Mewtwo EX', 'Psychic', 2000)
            """
        )
    )
    op.create_table(
        "collection",
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("card_id", sa.Integer, primary_key=True),
        sa.Column("quantity", sa.Integer, nullable=False),

        sa.ForeignKeyConstraint(["card_id"], ["cards.id"], name="fk_collection_card_id", ondelete='CASCADE'), #Foreign Key to Users
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_collection_user_id", ondelete='CASCADE'), #Foreign Key to Users
    )
    


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("collection")
    op.drop_table("cards")
    pass
