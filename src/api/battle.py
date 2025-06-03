from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlalchemy
from src.api import auth
from src import database as db
import numpy as np
import time
from src.api.collection import check_user_exists

router = APIRouter(
    prefix="/battle",
    tags=["battle"],
    dependencies=[Depends(auth.get_api_key)],
)

class BattleResponse(BaseModel):
    result: str
    prize: Optional[int] = 0

@router.post("/{user_id}/battle/{deck_name}", response_model=BattleResponse)
def battle(user_id: int, deck_name: str) -> BattleResponse:
    """
    Simulate a battle using the specified user's deck.

    Args:
        user_id (int): The ID of the user initiating the battle.
        deck_name (str): The name of the deck to battle with.

    Returns:
        BattleResponse: Result of the battle and prize coins if any.

    Raises:
        HTTPException 404 if the user or the deck does not exist.
        HTTPException 400 if the deck contains no cards.
    """
    start_time = time.time()  # Start timer
    
    check_user_exists(user_id)

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                SELECT id FROM decks 
                WHERE LOWER(deck_name) = LOWER(:deck_name) 
                  AND user_id = :user_id
            """),
            {"deck_name": deck_name, "user_id": user_id}
        ).fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="User's deck {deck_name} does not exist")

        deck_id = result[0]

        deck_contents = connection.execute(
            sqlalchemy.text("""
                SELECT d.card_name, c.price FROM deck_cards AS d
                INNER JOIN cards AS c ON c.name = d.card_name
                WHERE d.deck_id = :deck_id
            """),
            {"deck_id": deck_id}
        ).all()

    if not deck_contents:
        raise HTTPException(status_code=400, detail="Deck {deck_name} contains no cards.")

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

    win_prob = 0.01 * (30 + (avg_value * 0.4) + (highest_value * 0.2) + (lowest_value * 0.1))
    win_prob = max(0, min(1, win_prob))  # clamp to [0, 1]

    battle_result = np.random.choice(['Victory!', 'Defeat...'], p=[win_prob, 1 - win_prob])

    prize = 0
    if battle_result == 'Victory!':
        prize = 100
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text("""
                    UPDATE users
                    SET coins = coins + :prize
                    WHERE id = :user_id
                """),
                {"prize": prize, "user_id": user_id}
            )
    end_time = time.time()  # End timer
    elapsed_ms = (end_time - start_time) * 1000
    print(f"Completed in {elapsed_ms:.2f} ms")
    return BattleResponse(result=battle_result, prize=prize)
