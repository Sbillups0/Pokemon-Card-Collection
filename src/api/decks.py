from dataclasses import dataclass
import time
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db
from src.api.catalog import Card, Pack
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
        """
        Validates that the deck name is not empty.
        """
        if not value:
            raise ValueError("Deck name cannot be empty")
        return value

@router.post("/{user_id}/create_deck/{deck_name}")
def create_deck(user_id: int, deck_name: str, cards: List[str]):
    """
    Create a new deck for a specified user.

    Validation rules:
    - Exactly 5 cards must be included.
    - All cards must exist in the card database.
    - The deck name must be unique per user.
    - The user must exist.

    Args:
        user_id (int): ID of the user creating the deck.
        deck_name (str): Name of the new deck.
        cards (List[str]): List of exactly 5 card names to include.

    Raises:
        HTTPException 400: If deck size is not 5, deck name exists, or cards don't exist.
        HTTPException 404: If user does not exist.

    Returns:
        dict: Success message on deck creation.
    """
    start_time = time.time()  # Start timer
    with db.engine.begin() as connection:
        # Validate exact deck size
        if len(cards) != 5:
            raise HTTPException(status_code=400, detail="A deck must contain exactly 5 cards.")

        # Confirm user exists
        check_user_exists(user_id)

        # Check if the deck name is already taken for this user
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
                detail=f"A deck named '{deck_name}' already exists for this user."
            )
        
        # Get all decks for the user
        decks = connection.execute(
            sqlalchemy.text("""
                SELECT id, deck_name FROM decks
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).mappings().all()

        if len(decks) > 3:
            raise HTTPException(
                status_code=400,
                detail=f"User has too many decks (maximum allowed is 3). Decks are {decks}"
            )

        # Verify all cards exist in the card database
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
                detail=f"The following cards do not exist: {', '.join(invalid_cards)}."
            )
        # Check if there are any duplicate cards in the requested cards
        if len(set(cards)) < len(cards):
            raise HTTPException(
                status_code=408,
                detail="Deck cannot contain duplicate cards."
            )
        
        # Insert the new deck
        deck_id_row = connection.execute(
            sqlalchemy.text("""
                INSERT INTO decks (user_id, deck_name)
                VALUES (:user_id, :deck_name)
                RETURNING id
            """),
            {"user_id": user_id, "deck_name": deck_name}
        ).first()

        deck_id = deck_id_row.id

        # Associate each card with the new deck
        for card in cards:
            connection.execute(
                sqlalchemy.text("""
                    INSERT INTO deck_cards (deck_id, card_name)
                    VALUES (:deck_id, :card_name)
                """),
                {"deck_id": deck_id, "card_name": card}
            )
        end_time = time.time()  # End timer
        elapsed_ms = (end_time - start_time) * 1000
        print(f"Completed in {elapsed_ms:.2f} ms")
        return {"message": "Deck created successfully."}

@router.get("/{user_id}/decks")
def get_user_decks(user_id: int):
    """
    Retrieve all deck names created by a user.

    Args:
        user_id (int): The user's ID.

    Raises:
        HTTPException 404: If user does not exist, no decks found, or user has more than 3 decks.

    Returns:
        List[str]: List of deck names owned by the user.
    """
    start_time = time.time()  # Start timer
    with db.engine.begin() as connection:
        # Check user existence
        check_user_exists(user_id)

        # Get all decks for the user
        decks = connection.execute(
            sqlalchemy.text("""
                SELECT id, deck_name FROM decks
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).mappings().all()

        if not decks:
            raise HTTPException(
                status_code=404,
                detail=f"No decks found for user with ID {user_id}."
            )

        if len(decks) > 3:
            raise HTTPException(
                status_code=400,
                detail=f"User has too many decks (maximum allowed is 3). Decks are {decks}"
            )

        # Get cards for each deck
        result = {}
        for deck in decks:
            deck_id = deck["id"]
            deck_name = deck["deck_name"]

            cards = connection.execute(
                sqlalchemy.text("""
                    SELECT card_name FROM deck_cards
                    WHERE deck_id = :deck_id
                """),
                {"deck_id": deck_id}
            ).scalars().all()

            result[deck_name] = cards

        end_time = time.time()  # End timer
        elapsed_ms = (end_time - start_time) * 1000
        print(f"Completed in {elapsed_ms:.2f} ms")

        return result
    
@router.delete("/{user_id}/decks/{deck_name}")
def delete_deck(user_id: int, deck_name: str):
    """
    Delete a specific deck for a user.
    """
    with db.engine.begin() as connection:
        # Confirm deck exists
        deck = connection.execute(
            sqlalchemy.text("""
                SELECT id FROM decks
                WHERE user_id = :user_id AND deck_name = :deck_name
            """),
            {"user_id": user_id, "deck_name": deck_name}
        ).first()

        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found.")

        # Delete the deck cards first (if you have a deck_cards table)
        connection.execute(
            sqlalchemy.text("""
                DELETE FROM deck_cards WHERE deck_id = :deck_id
            """),
            {"deck_id": deck.id}
        )

        # Delete the deck itself
        connection.execute(
            sqlalchemy.text("""
                DELETE FROM decks WHERE id = :deck_id
            """),
            {"deck_id": deck.id}
        )

    return {"message": f"Deck '{deck_name}' deleted successfully."}
