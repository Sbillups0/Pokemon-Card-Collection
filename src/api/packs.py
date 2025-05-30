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

class RecommendedPack(BaseModel):
    Pack: str
    Currently_Missing: int

class PackOpenResult(BaseModel):
    remaining_coins: int
    opened_packs: List[PackOpened]

def check_user_exists(user_id: int):
     with db.engine.begin() as connection:
        existing_user = connection.execute(sqlalchemy.text("""
            SELECT id FROM users WHERE id = :user_id
        """), {"user_id": user_id}).scalar_one_or_none()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User does not exist")

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
                WHERE LOWER(name) = LOWER(:pack_name)
            """),
            {"pack_name": pack_name}
        ).fetchone()

        if not pack_data:
            raise HTTPException(status_code=404, detail="Pack not found")

        return pack_data[0]

@router.get("/{user_id}/reccommended_pack", tags=["packs"], response_model=RecommendedPack)
def recommended_pack(user_id: int):
    #Looks at a user's current collection, and the total distrubition of cards in each pack, assigning a value to each pack based
    #on how many cards the user owns from it, returning whichever pack has the highest value.
    check_user_exists(user_id)
    with db.engine.begin() as connection:
        pack_list = connection.execute(sqlalchemy.text("SELECT name FROM packs")).scalars().all()
    
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    p.id AS pack_id,
                    p.name AS pack_name,
                    p.price AS cost,
                    COUNT(DISTINCT CASE WHEN col.user_id = :user_id THEN c.id END) AS unique_cards_owned
                FROM packs p
                LEFT JOIN cards c ON c.pack_id = p.id
                LEFT JOIN collection col ON col.card_id = c.id AND col.user_id = :user_id
                GROUP BY p.id, p.name
                ORDER BY p.id
                """     
        ), {"user_id": user_id}).fetchall()
        min = 99999999
        for row in results:
            print(f"Pack: {row.pack_name}, Unique Cards Owned: {row.unique_cards_owned}")
            if row.unique_cards_owned < min:
                min = row.unique_cards_owned
                pack = row

    return RecommendedPack(Pack=pack.pack_name,Currently_Missing=20 - pack.unique_cards_owned)

@router.post("/open_packs/{user_id}/{pack_name}/{pack_quantity}", tags=["packs"], response_model=PackOpenResult)
def open_packs(user_id: int, 
               pack_name: str, 
               pack_quantity: int = Path(..., gt=0, description="Number of packs to purchase (must be > 0)")):
    if pack_quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Pack quantity must be a positive integer"
        )
    check_user_exists(user_id)
    

    with db.engine.begin() as connection:
        pack_id = check_pack_exists(pack_name)
        # 1. Check if user has enough packs to open
        owned_packs = connection.execute(
            sqlalchemy.text("""
                SELECT quantity FROM inventory
                WHERE user_id = :user_id AND pack_id = :pack_id
            """),
            {"user_id": user_id, "pack_id": pack_id}
        ).scalar_one_or_none()
        
       

        if owned_packs is None or owned_packs < pack_quantity:
            raise HTTPException(status_code=404, detail="Not enough packs in inventory")

        # 2. Update inventory to reflect packs opened
        connection.execute(
            sqlalchemy.text("""
                UPDATE inventory
                SET quantity = quantity - :pack_quantity
                WHERE user_id = :user_id AND pack_id = :pack_id
            """),
            {"user_id": user_id, "pack_quantity": pack_quantity, "pack_id": pack_id}
        )

        # 3. Fetch all cards from the pack (once instead of in every loop)
        packs = connection.execute(
            sqlalchemy.text("""
                SELECT cards.name, cards.price FROM cards
                WHERE cards.pack_id = :pack_id
                ORDER BY cards.price ASC
            """),
            {"pack_id": pack_id}
        ).all()

        # Get remaining coin balance
        remaining_coins = connection.execute(
            sqlalchemy.text("""
                SELECT coins FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        ).scalar_one()


        # 4. Open packs and collect cards
        opened_packs = []
        for i in range(pack_quantity):
            card_list = []
            for j in range(5):
                chosen_card = weighted_random_choice(packs)

                # Insert or update collection
                connection.execute(
                    sqlalchemy.text("""
                        INSERT INTO collection (user_id, card_id, quantity)
                        VALUES (:user_id, (SELECT id FROM cards WHERE name = :card_name), 1)
                        ON CONFLICT (user_id, card_id)
                        DO UPDATE SET quantity = collection.quantity + 1
                    """),
                    {"user_id": user_id, "card_name": chosen_card}
                )
                card_list.append(chosen_card)

            opened_packs.append(PackOpened(name=f"{pack_name} #{i + 1}", cards=card_list))

    return PackOpenResult(remaining_coins=remaining_coins, opened_packs=opened_packs)


@router.post("/purchase_packs/{user_id}/{pack_name}/{pack_quantity}", tags=["packs"], response_model=Checkout)
def purchase_packs(user_id: int,
                   pack_name: str, 
                   pack_quantity: int = Path(..., gt=0, description="Number of packs to purchase (must be > 0)")):
    """The user given by the user_id gives the name of a specific pack and the number they'd
        like to purchase. The price is subtracted from their gold and the packs are added to 
        their inventory."""

    if pack_quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Pack quantity must be a positive integer"
        )
     # 1. Check user existence early
    check_user_exists(user_id)
     # 2. Check pack existence and get pack_id
    pack_id = check_pack_exists(pack_name)
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
            raise HTTPException(
                status_code=400,
                detail=f"Not enough coins. Current balance: {user_coins}, required: {total_cost}"
            )

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
