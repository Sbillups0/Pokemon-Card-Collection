from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db
from src.api.catalog import Card, Pack
from fastapi import HTTPException
from src.api.collection import check_user_exists


router = APIRouter(
    prefix="/decks",
    tags=["decks"],
    dependencies=[Depends(auth.get_api_key)],
)

class Deck(BaseModel):
    deck_name: str
    cards: List[str] = Field(min_items=5, max_items=5)

    @field_validator("deck_name")
    def validate_deck_name(cls, value):
        if not value:
            raise ValueError("Deck name cannot be empty")
        return value

@router.post("/users/{user_id}/create_deck/{deck_name}")
def create_deck(user_id: int, deck_name: str, cards: List[str]):
    
    with db.engine.begin() as connection:
        if len(cards) != 5:
            raise HTTPException(status_code=400, detail="A deck must contain exactly 5 cards")

        # Check user exists
        check_user_exists(user_id)

        # Check if deck already exists
        existing_deck = connection.execute(
            sqlalchemy.text("""
                SELECT COUNT(*) FROM decks
                WHERE user_id = :user_id AND deck_name = :deck_name
            """),
            {"user_id": user_id, "deck_name": deck_name}
        ).scalar()

        if existing_deck:
            raise HTTPException(
                status_code=400,
                detail=f"A deck with the name '{deck_name}' already exists for this user"
            )

        # Check if cards exist
        placeholders = ", ".join([f":card_{i}" for i in range(len(cards))])
        params = {f"card_{i}": card for i, card in enumerate(cards)}

        query = f"""
            SELECT name FROM cards
            WHERE name IN ({placeholders})
        """
        result = connection.execute(sqlalchemy.text(query), params)
        existing_cards = result.scalars().all()

        invalid_cards = [card for card in cards if card not in existing_cards]
        if invalid_cards:
            raise HTTPException(
                status_code=400,
                detail=f"The following cards do not exist: {', '.join(invalid_cards)}"
            )

        # Create the deck and get its ID
        deck_id_row = connection.execute(
            sqlalchemy.text("""
                INSERT INTO decks (user_id, deck_name)
                VALUES (:user_id, :deck_name)
                RETURNING id
            """),
            {"user_id": user_id, "deck_name": deck_name}
        ).first()

        deck_id = deck_id_row.id
        

        # Add cards to the deck
        for card in cards:
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO deck_cards (deck_id, card_name)
                    VALUES (:deck_id, :card_name)
                """),
                {"deck_id": deck_id, "card_name": card}
            )
        return {"message": "Deck created successfully"}

@router.get("/users/{user_id}/decks")
def get_user_decks(user_id: int):
    with db.engine.begin() as connection:
        # Check user exists (optional but safe)
        if not check_user_exists(user_id):
            raise HTTPException(status_code=404, detail="User not found")

        deck_names = connection.execute(
            sqlalchemy.text("""
                SELECT deck_name FROM decks
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).scalars().all()

        if not deck_names:
            raise HTTPException(status_code=404, detail="No decks found for this user")
        
        if len(deck_names) > 3:
            raise HTTPException(status_code=404, detail="User has too many decks (max 3)")
        
        return deck_names
