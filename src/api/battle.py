from dataclasses import dataclass
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db
import numpy as np
from src.api.collection import check_user_exists

router = APIRouter(
    prefix="/battle",
    tags=["battle"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/{user_id}/battle/{deck_name}", tags=["battle"], response_model=str)
def battle(user_id: int, deck_name: str) -> str:
    """
    Simulate a battle using the specified user's deck.

    Args:
        user_id (int): The ID of the user initiating the battle.
        deck_name (str): The name of the deck to battle with.

    Returns:
        str: The battle result, either 'Victory!' or 'Defeat...'.

    Raises:
        HTTPException 404 if the user or the deck does not exist.
        HTTPException 400 if the deck contains no cards.
    """
    # Verify that the user exists
    check_user_exists(user_id)

    with db.engine.begin() as connection:
        # Get deck ID by deck name
        result = connection.execute(
            sqlalchemy.text("SELECT id FROM decks WHERE deck_name = :deck_name"),
            {"deck_name": deck_name}
        ).fetchone()
    
        if result is None:
            raise HTTPException(status_code=404, detail="Deck does not exist")
    
        deck_id = result[0]
    
        # Get cards in the deck along with their prices
        deck_contents = connection.execute(
            sqlalchemy.text(
                """
                SELECT d.card_name, c.price FROM deck_cards AS d
                INNER JOIN cards AS c ON c.name = d.card_name
                WHERE d.deck_id = :deck_id
                """
            ),
            {"deck_id": deck_id}
        ).all()

    if not deck_contents:
        raise HTTPException(status_code=400, detail="Deck contains no cards.")

    # Calculate deck card value statistics for battle logic
    MAX_CARD_PRICE = 100
    value_sum = 0
    highest_value = 0
    lowest_value = MAX_CARD_PRICE

    for _, price in deck_contents:
        card_value = min(price, MAX_CARD_PRICE)
        highest_value = max(highest_value, card_value)
        lowest_value = min(lowest_value, card_value)
        value_sum += card_value

    avg_value = value_sum / len(deck_contents)

    # Calculate winning probability (scaled)
    win_prob = 0.01 * (30 + (avg_value * 0.4) + (highest_value * 0.2) + (lowest_value * 0.1))

    # Simulate battle outcome using weighted random choice
    battle_result = np.random.choice(['Victory!', 'Defeat...'], p=[win_prob, 1 - win_prob])

    if battle_result == 'Victory!':
        # Reward user coins for winning
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE users
                    SET coins = coins + :prize
                    WHERE id = :user_id
                    """
                ),
                {"prize": 100, "user_id": user_id}
            )

    return battle_result
