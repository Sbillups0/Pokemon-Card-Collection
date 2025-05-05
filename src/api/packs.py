from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List

import sqlalchemy
from src.api import auth
from src import database as db
from src.api.catalog import Pack

router = APIRouter(
    prefix="/packs",
    tags=["packs"],
    dependencies=[Depends(auth.get_api_key)],
)

"""class Pack(BaseModel):
    name: str
    price: int"""

@router.post("/users/{user_id}/purchase_packs/{pack_name}/{pack_quantity}", tags=["packs"], status_code=status.HTTP_204_NO_CONTENT)
def purchase_packs(user_id: int, pack_name: str, pack_quantity: int):
    """The user given by the user_id gives the name of a specific pack and the number they'd
        like to purchase. The price is subtracted from their gold and the packs are added to 
        their inventory."""
    
    with db.engine.begin() as connection:
        pack_data = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, price FROM packs
                WHERE name = :pack_name
                """
            ),
            [{"pack_name": pack_name}],
        ).one()
        packs_owned = connection.execute(
            sqlalchemy.text(
                """
                SELECT pack_id FROM inventory
                WHERE user_id = :user_id
                """
            ),
            [{"user_id": user_id}],
        )
    
        pack_choice = pack_data[0]
        total_coins = pack_data[1] * pack_quantity
        if pack_choice in packs_owned:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE inventory SET 
                    quantity = quantity + :pack_quantity
                    WHERE pack_id = :pack_choice
                    """
                ),
                [{"pack_quantity": pack_quantity,
                    "pack_choice": pack_choice}]
            )
        else:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO inventory
                    VALUES (:user_id, :pack_id, :quantity)
                    """
                ),
                [{"user_id": user_id, 
                "pack_id": pack_choice,
                "quantity": pack_quantity}],
            )

        connection.execute(
            sqlalchemy.text(
                """
                UPDATE users SET 
                coins = coins + :total_coins
                WHERE pack_id = :pack_choice
                """
            ),
            [{"total_coins": total_coins}]
        )
    
    pass
