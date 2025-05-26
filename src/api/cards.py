from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/cards",
    tags=["cards"],
)


def check_user_exists(user_id: int):
     with db.engine.begin() as connection:
        existing_user = connection.execute(sqlalchemy.text("""
            SELECT id FROM users WHERE id = :user_id
        """), {"user_id": user_id}).scalar_one_or_none()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User does not exist")



@router.get("/allcards")
def get_all_cards():
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
    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("""
            SELECT 
                cards.name,
                cards.type,
                cards.price,
                packs.name AS pack
            FROM cards
            JOIN packs ON cards.pack_id = packs.id
            WHERE cards.name = :card_name
        """), {"card_name": card_name}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Card not found")

        return {
            "name": result.name,
            "price": result.price,
            "type": result.type,
            "pack": result.pack
        }


class SellByNameRequest(BaseModel):
    quantity: int

@router.post("/users/{user_id}/sell/{card_name}")
def sell_card_by_name(user_id: int, card_name: str, req: SellByNameRequest):
    with db.engine.begin() as conn:
        # Check user exists
        check_user_exists(user_id)
        # Get card_id and price
        card = conn.execute(sqlalchemy.text("""
            SELECT id, price FROM cards WHERE name = :card_name
        """), {"card_name": card_name}).fetchone()
        
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        card_id = card.id
        card_price = card.price

        # Check user owns enough cards and update in one step
        updated_row = conn.execute(sqlalchemy.text("""
            UPDATE collection
            SET quantity = quantity - :qty
            WHERE user_id = :user_id AND card_id = :card_id AND quantity >= :qty
            RETURNING quantity
        """), {
            "qty": req.quantity, "user_id": user_id, "card_id": card_id
        }).fetchone()

        if not updated_row:
            raise HTTPException(status_code=400, detail="Not enough cards to sell")

        # Delete the row if quantity reaches zero
        if updated_row.quantity == 0:
            conn.execute(sqlalchemy.text("""
                DELETE FROM collection
                WHERE user_id = :user_id AND card_id = :card_id
            """), {"user_id": user_id, "card_id": card_id})

        # Update user's coins
        total_value = req.quantity * card_price
        conn.execute(sqlalchemy.text("""
            UPDATE users SET coins = coins + :value WHERE id = :user_id
        """), {"value": total_value, "user_id": user_id})

    return {
        "message": f"Sold {req.quantity} {card_name} for {total_value} coins"
    }
