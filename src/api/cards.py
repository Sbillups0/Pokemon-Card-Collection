from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, conint
from typing import List
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/cards",
    tags=["cards"],
)

class SellByNameRequest(BaseModel):
    quantity: conint(gt=0)  # quantity must be a positive integer

def check_user_exists(user_id: int):
    """
    Verify that a user with the given user_id exists in the database.
    
    Raises:
        HTTPException 404 if user does not exist.
    """
    with db.engine.begin() as connection:
        existing_user = connection.execute(sqlalchemy.text("""
            SELECT id FROM users WHERE id = :user_id
        """), {"user_id": user_id}).scalar_one_or_none()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User does not exist")

@router.get("/allcards")
def get_all_cards():
    """
    Retrieve all cards along with their type, price, and the pack they belong to.

    Returns:
        List of dictionaries, each containing card name, type, price, and pack name.

    Raises:
        HTTPException 404 if no cards are found in the database.
    """
    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("""
            SELECT 
                cards.name,
                cards.type,
                cards.price,
                packs.name AS pack
            FROM cards
            JOIN packs ON cards.pack_id = packs.id
        """)).fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="No cards found")

        return [
            {
                "name": row.name,
                "price": row.price,
                "type": row.type,
                "pack": row.pack
            } for row in result
        ]

@router.get("/{card_name}")
def get_card_by_name(card_name: str):
    """
    Retrieve details of a specific card by its name (case-insensitive).

    Args:
        card_name (str): Name of the card to retrieve.

    Returns:
        Dictionary with card details: name, type, price, and pack.

    Raises:
        HTTPException 404 if the card is not found.
    """
    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("""
            SELECT 
                cards.name,
                cards.type,
                cards.price,
                packs.name AS pack
            FROM cards
            JOIN packs ON cards.pack_id = packs.id
            WHERE LOWER(cards.name) = LOWER(:card_name)
        """), {"card_name": card_name}).fetchone()

        if not result:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Card '{card_name}' not found. Check for typos or try another name."
                )
            )

        return {
            "name": result.name,
            "price": result.price,
            "type": result.type,
            "pack": result.pack
        }

@router.post("/sell/{user_id}/{card_name}")
def sell_card_by_name(user_id: int, card_name: str, req: SellByNameRequest):
    """
    Sell a specified quantity of a card by its name from the user's collection.
    
    Args:
        user_id (int): ID of the user selling the card.
        card_name (str): Name of the card to sell.
        req (SellByNameRequest): Request body containing quantity to sell.

    Returns:
        Message confirming successful sale, coins earned, and remaining quantity.

    Raises:
        HTTPException 404 if the user or card does not exist.
        HTTPException 400 if the card is in the user's decks or if quantity is insufficient.
    """
    with db.engine.begin() as conn:
        # Verify user exists
        check_user_exists(user_id)

        # Case-insensitive card lookup for id and price
        card = conn.execute(sqlalchemy.text("""
            SELECT id, price FROM cards WHERE LOWER(name) = LOWER(:card_name)
        """), {"card_name": card_name}).fetchone()

        if not card:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Card not found. Make sure the card name is correctly spelled and capitalized."
                )
            )

        card_id = card.id
        card_price = card.price

        # Check if card is in any decks owned by user (by card_id)
        card_in_deck = conn.execute(sqlalchemy.text("""
            SELECT dc.id FROM deck_cards dc
            JOIN decks d ON dc.deck_id = d.id
            WHERE d.user_id = :user_id AND LOWER(dc.card_name) = LOWER(:card_name)
        """), {"user_id": user_id, "card_id": card_id}).fetchone()

        if card_in_deck:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot sell '{card_name}' because it is currently in one or more of your decks. Remove it from all decks before selling."
            )

        # Check if user owns enough quantity to sell
        owned = conn.execute(sqlalchemy.text("""
            SELECT quantity FROM collection
            WHERE user_id = :user_id AND card_id = :card_id
        """), {"user_id": user_id, "card_id": card_id}).scalar()

        if not owned or owned < req.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough cards to sell. You own {owned or 0} of '{card_name}'."
            )

        # Decrease quantity or delete record if zero
        updated_row = conn.execute(sqlalchemy.text("""
            UPDATE collection
            SET quantity = quantity - :qty
            WHERE user_id = :user_id AND card_id = :card_id AND quantity >= :qty
            RETURNING quantity
        """), {
            "qty": req.quantity, "user_id": user_id, "card_id": card_id
        }).fetchone()

        if updated_row.quantity == 0:
            conn.execute(sqlalchemy.text("""
                DELETE FROM collection
                WHERE user_id = :user_id AND card_id = :card_id
            """), {"user_id": user_id, "card_id": card_id})

        # Add coins to user's balance
        total_value = req.quantity * card_price
        conn.execute(sqlalchemy.text("""
            UPDATE users SET coins = coins + :value WHERE id = :user_id
        """), {"value": total_value, "user_id": user_id})

    return {
        "message": f"Sold {req.quantity} '{card_name}' for {total_value} coins",
        "coins_earned": total_value,
        "remaining_quantity": updated_row.quantity
    }
