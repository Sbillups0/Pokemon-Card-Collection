from dataclasses import dataclass
from fastapi import APIRouter, Depends, status, Path, HTTPException
from pydantic import BaseModel
from typing import List
import sqlalchemy
import random
import math

from src.api import auth
from src import database as db
from src.api.catalog import Pack
from src.api.collection import check_user_exists

router = APIRouter(
    prefix="/packs",
    tags=["packs"],
    dependencies=[Depends(auth.get_api_key)],
)



class Checkout(BaseModel):
    """Model for representing the result of a pack purchase."""
    pack: str
    total_spent: int


class PackOpened(BaseModel):
    """Model for a single opened pack and the cards it contains."""
    name: str
    cards: List[str]


class RecommendedPack(BaseModel):
    """Model representing a recommended pack and how many cards the user is missing from it."""
    Pack: str
    Currently_Missing: int


class PackOpenResult(BaseModel):
    """Model representing the result of opening multiple packs."""
    remaining_coins: int
    opened_packs: List[PackOpened]



def weighted_random_choice(item_list):
    """
    Selects an item from the list with a bias toward lower-priced items.

    Args:
        item_list (List[Tuple[str, int]]): List of (name, price) tuples.

    Returns:
        str: The name of the selected item.
    """
    max_price = max(price for _, price in item_list)
    weights = [math.sqrt(max_price - price + 1) for _, price in item_list]
    names = [name for name, _ in item_list]
    return random.choices(names, weights=weights, k=1)[0]


def check_pack_exists(pack_name: str):
    """
    Ensures a pack with the given name exists in the database.

    Args:
        pack_name (str): Name of the pack.

    Returns:
        int: The ID of the pack.

    Raises:
        HTTPException: If the pack is not found.
    """
    with db.engine.begin() as connection:
        pack = connection.execute(
            sqlalchemy.text("SELECT id FROM packs WHERE LOWER(name) = LOWER(:pack_name)"),
            {"pack_name": pack_name}
        ).fetchone()
    if not pack:
        raise HTTPException(
            status_code=404, 
            detail=f"Pack '{pack_name}' not found. Please check the name and try again."
        )
    return pack[0]



@router.get("/{user_id}/recommended_pack", tags=["packs"], response_model=RecommendedPack)
def recommended_pack(user_id: int):
    """
    Recommends a pack to the user where they are missing the most cards.

    Args:
        user_id (int): ID of the user.

    Returns:
        RecommendedPack: The pack with the most missing cards.
    """
    check_user_exists(user_id)
    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text("""
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
            """),
            {"user_id": user_id}
        ).fetchall()

        min_cards_owned = float('inf')
        recommended = None
        for row in results:
            if row.unique_cards_owned < min_cards_owned:
                min_cards_owned = row.unique_cards_owned
                recommended = row

    return RecommendedPack(Pack=recommended.pack_name, Currently_Missing=20 - recommended.unique_cards_owned)


@router.post("/open_packs/{user_id}/{pack_name}/{pack_quantity}", tags=["packs"], response_model=PackOpenResult)
def open_packs(user_id: int, pack_name: str, pack_quantity: int = Path(..., gt=0, description="Must be > 0")):
    """
    Opens a number of packs and adds the drawn cards to the user's collection.

    Args:
        user_id (int): ID of the user.
        pack_name (str): Name of the pack to open.
        pack_quantity (int): Number of packs to open.

    Returns:
        PackOpenResult: Cards drawn and updated coin balance.

    Raises:
        HTTPException: If user does not have enough packs or pack does not exist.
    """
    if not isinstance(pack_quantity, int) or pack_quantity <= 0:
        raise HTTPException(status_code=422, detail="Pack quantity must be a positive integer.")

    check_user_exists(user_id)

    with db.engine.begin() as connection:
        pack_id = check_pack_exists(pack_name)

        owned_packs = connection.execute(
            sqlalchemy.text("""
                SELECT quantity FROM inventory
                WHERE user_id = :user_id AND pack_id = :pack_id
            """),
            {"user_id": user_id, "pack_id": pack_id}
        ).scalar_one_or_none()

        if owned_packs is None or owned_packs < pack_quantity:
            raise HTTPException(
                status_code=409,
                detail=f"User only has {owned_packs or 0} packs of '{pack_name}' but requested {pack_quantity}"
            )

        connection.execute(
            sqlalchemy.text("""
                UPDATE inventory
                SET quantity = quantity - :pack_quantity
                WHERE user_id = :user_id AND pack_id = :pack_id
            """),
            {"user_id": user_id, "pack_quantity": pack_quantity, "pack_id": pack_id}
        )

        packs = connection.execute(
            sqlalchemy.text("""
                SELECT cards.name, cards.price FROM cards
                WHERE cards.pack_id = :pack_id
                ORDER BY cards.price ASC
            """),
            {"pack_id": pack_id}
        ).all()

        remaining_coins = connection.execute(
            sqlalchemy.text("""
                SELECT coins FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        ).scalar_one()

        opened_packs = []
        for i in range(pack_quantity):
            card_list = []
            for _ in range(5):
                chosen_card = weighted_random_choice(packs)
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
def purchase_packs(user_id: int, pack_name: str, pack_quantity: int = Path(..., gt=0, description="Must be > 0")):
    """
    Allows a user to purchase a specific quantity of packs using in-game coins.

    Args:
        user_id (int): ID of the user.
        pack_name (str): Name of the pack to purchase.
        pack_quantity (int): Number of packs to purchase.

    Returns:
        Checkout: Confirmation of purchase with total amount spent.

    Raises:
        HTTPException: If the user has insufficient coins or pack does not exist.
    """
    if not isinstance(pack_quantity, int) or pack_quantity <= 0:
        raise HTTPException(status_code=422, detail="Pack quantity must be a positive integer.")

    check_user_exists(user_id)
    pack_id = check_pack_exists(pack_name)

    with db.engine.begin() as connection:
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
                status_code=409,
                detail=f"Not enough coins. Current balance: {user_coins}, required: {total_cost}"
            )

        inventory_data = connection.execute(
            sqlalchemy.text("""
                SELECT quantity FROM inventory
                WHERE user_id = :user_id AND pack_id = :pack_id
            """),
            {"user_id": user_id, "pack_id": pack_id}
        ).fetchone()

        if inventory_data:
            connection.execute(
                sqlalchemy.text("""
                    UPDATE inventory
                    SET quantity = quantity + :pack_quantity
                    WHERE user_id = :user_id AND pack_id = :pack_id
                """),
                {"pack_quantity": pack_quantity, "user_id": user_id, "pack_id": pack_id}
            )
        else:
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO inventory (user_id, pack_id, quantity)
                    VALUES (:user_id, :pack_id, :quantity)
                """),
                {"user_id": user_id, "pack_id": pack_id, "quantity": pack_quantity}
            )

        connection.execute(
            sqlalchemy.text("""
                UPDATE users
                SET coins = coins - :total_cost
                WHERE id = :user_id
            """),
            {"total_cost": total_cost, "user_id": user_id}
        )

    return Checkout(pack=pack_name, total_spent=total_cost)
