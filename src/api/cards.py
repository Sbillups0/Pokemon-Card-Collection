from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/cards",
    tags=["cards"],
)

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
        # Get card_id and cost
        card = conn.execute(sqlalchemy.text("""
            SELECT id, price FROM cards WHERE name = :card_name
        """), {"card_name": card_name}).fetchone()

        if not card:
            raise HTTPException(status_code=404, detail="Card not found")

        card_id = card.id
        card_cost = card.price
        print("Card ID:" + str(card_id))
        print("Card Cost:" + str(card_cost))
        # Check user's collection
        owned = conn.execute(sqlalchemy.text("""
            SELECT quantity FROM collection
            WHERE user_id = :user_id AND card_id = :card_id
        """), {"user_id": user_id, "card_id": card_id}).fetchone()

        if not owned or owned.quantity < req.quantity:
            raise HTTPException(status_code=400, detail="Not enough cards to sell")
        # Update collection
        if owned.quantity == req.quantity:
            conn.execute(sqlalchemy.text("""
                DELETE FROM collection
                WHERE user_id = :user_id AND card_id = :card_id
            """), {"user_id": user_id, "card_id": card_id})
        else:
            conn.execute(sqlalchemy.text("""
                UPDATE collection
                SET quantity = quantity - :qty
                WHERE user_id = :user_id AND card_id = :card_id
            """), {"qty": req.quantity, "user_id": user_id, "card_id": card_id})

        user = conn.execute(sqlalchemy.text("""
            SELECT coins FROM users WHERE id = :user_id
        """), {"user_id": user_id}).fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user's coins
        total_value = req.quantity * card_cost
        result = conn.execute(sqlalchemy.text("""
            UPDATE users SET coins = coins + :value WHERE id = :user_id
        """), {"value": total_value, "user_id": user_id})

    return {
        "message": f"Sold {req.quantity} {card_name} for {total_value} coins"
    }

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