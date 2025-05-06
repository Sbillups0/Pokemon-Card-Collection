from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
from fastapi import HTTPException

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

class Checkout(BaseModel):
    pack: str
    total_spent: int

@router.post("/users/{user_id}/purchase_packs/{pack_name}/{pack_quantity}", tags=["packs"], status_code=status.HTTP_204_NO_CONTENT)
def purchase_packs(user_id: int, pack_name: str, pack_quantity: int):
    """The user given by the user_id gives the name of a specific pack and the number they'd
        like to purchase. The price is subtracted from their gold and the packs are added to 
        their inventory."""
    
    with db.engine.begin() as connection:
        # 1. Fetch pack info
        pack_data = connection.execute(
            sqlalchemy.text("""
                SELECT id, price FROM packs
                WHERE name = :pack_name
            """),
            {"pack_name": pack_name}
        ).fetchone()

        if not pack_data:
            raise HTTPException(status_code=404, detail="Pack not found")

        pack_id, pack_price = pack_data
        total_cost = pack_price * pack_quantity

        # 2. Check user has enough coins
        user_data = connection.execute(
            sqlalchemy.text("""
                SELECT coins FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        user_coins = user_data[0]
        if user_coins < total_cost:
            raise HTTPException(status_code=400, detail="Not enough coins")

        # 3. Check if pack already in inventory
        inventory_data = connection.execute(
            sqlalchemy.text("""
                SELECT quantity FROM inventory
                WHERE user_id = :user_id AND pack_id = :pack_id
            """),
            {"user_id": user_id, "pack_id": pack_id}
        ).fetchone()

        if inventory_data:
            # Update existing inventory
            connection.execute(
                sqlalchemy.text("""
                    UPDATE inventory
                    SET quantity = quantity + :pack_quantity
                    WHERE user_id = :user_id AND pack_id = :pack_id
                """),
                {"pack_quantity": pack_quantity, "user_id": user_id, "pack_id": pack_id}
            )
        else:
            # Insert new inventory record
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO inventory (user_id, pack_id, quantity)
                    VALUES (:user_id, :pack_id, :quantity)
                """),
                {"user_id": user_id, "pack_id": pack_id, "quantity": pack_quantity}
            )

        # 4. Subtract coins
        connection.execute(
            sqlalchemy.text("""
                UPDATE users
                SET coins = coins - :total_cost
                WHERE id = :user_id
            """),
            {"total_cost": total_cost, "user_id": user_id}
        )
        return Checkout(pack = name, total_spent = total_cost)
