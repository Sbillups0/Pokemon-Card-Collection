from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
from fastapi import HTTPException

import sqlalchemy
from src.api import auth
from src import database as db
from src.api.catalog import Pack
import random 
import math
from src.api.collection import check_user_exists

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

class PackOpened(BaseModel):
    name: str
    cards: List[str]

def weighted_random_choice(item_list):
    # Get the maximum price to invert weights
    max_price = max(price for _, price in item_list)

    # Create weights: lower price = higher weight
    weights = [math.sqrt(max_price - price + 1) for _, price in item_list]

    # Extract names
    names = [name for name, _ in item_list]

    # Randomly choose based on weights
    chosen = random.choices(names, weights=weights, k=1)[0]
    return chosen

def check_pack_exists(pack_name: str):
    with db.engine.begin() as connection:
        pack_data = connection.execute(
            sqlalchemy.text("""
                SELECT id FROM packs
                WHERE name = :pack_name
            """),
            {"pack_name": pack_name}
        ).fetchone()

        if not pack_data:
            raise HTTPException(status_code=404, detail="Pack not found")

        return pack_data[0]

@router.post("/users/{user_id}/open_packs/{pack_name}/{pack_quantity}", tags=["packs"], response_model = List[PackOpened])
def open_packs(user_id: int, pack_name: str, pack_quantity: int):
        check_user_exists(user_id)
        check_pack_exists(pack_name)
        #1 Checks if user has enough packs to open
        with db.engine.begin() as connection:
            owned_packs = connection.execute(
                sqlalchemy.text("""
                    SELECT quantity FROM inventory
                    WHERE user_id = :user_id AND pack_id = (SELECT id FROM packs WHERE name = :pack_name)
                """),
                {"user_id": user_id, "pack_name": pack_name}
            ).scalar_one_or_none()

            if owned_packs < pack_quantity:
                raise HTTPException(status_code=404, detail="Not enough packs in inventory")
            else:
                # 2. Update inventory to reflect packs opened
                connection.execute(
                    sqlalchemy.text("""
                        UPDATE inventory
                        SET quantity = quantity - :pack_quantity
                        WHERE user_id = :user_id AND pack_id = (SELECT id FROM packs WHERE name = :pack_name)
                    """),
                    {"user_id": user_id, "pack_quantity": pack_quantity, "pack_name": pack_name}
                )
        #2 Opens packs for number of packs opened
        opened_packs = []
        for i in range(pack_quantity):
            with db.engine.begin() as connection:
                packs = connection.execute(
                    sqlalchemy.text("""
                        SELECT cards.name, cards.price FROM cards
                        LEFT JOIN packs ON cards.pack_id = packs.id
                        WHERE packs.name = :pack_name
                        ORDER BY cards.price asc"""
                    ),[{"pack_name": pack_name}]
                ).all()

                card_list = []
                for j in range(5):
                    # Get a random card from the pack
                    chosen_card = weighted_random_choice(packs)
                    # Insert into collection, updating quantity if it already exists
                    connection.execute(
                        sqlalchemy.text("""
                            INSERT INTO collection (user_id, card_id, quantity) VALUES (:user_id, (SELECT id FROM cards WHERE name = :card_name), 1)
                            ON CONFLICT (user_id, card_id) DO UPDATE SET quantity = collection.quantity + 1
                                        """
                        ),[{"user_id": user_id, "card_name": chosen_card}]
                    )
                    # Add the chosen card to card_list
                    card_list.append(chosen_card)
                #Passes chosen cards to PackOpened for certain pack
                opened_packs.append(PackOpened(name=pack_name+ ' #' + str(i+1), cards=card_list))
                
                   
        return opened_packs


@router.post("/users/{user_id}/purchase_packs/{pack_name}/{pack_quantity}", tags=["packs"], response_model=Checkout)
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
        return Checkout(pack = pack_name, total_spent = total_cost)
