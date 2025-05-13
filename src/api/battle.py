from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
from fastapi import HTTPException

import sqlalchemy
from src.api import auth
from src import database as db
import random 
import math
import numpy as np
from src.api.collection import check_user_exists

router = APIRouter(
    prefix="/battle",
    tags=["battle"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/users/{user_id}/battle/{deck_name}", tags=["battle"], response_model=str)
def battle(user_id: int, deck_name: str) -> str:
    check_user_exists(user_id)
    with db.engine.begin() as connection:
        deck_id = connection.execute(
                sqlalchemy.text(
                    "SELECT id FROM decks WHERE deck_name = :deck_name"
                ),
                [{"deck_name": deck_name}]
            ).one()
        if deck_id is None:
            raise HTTPException(status_code=404, detail="Deck does not exist")
        deck_contents = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT d.card_name, c.price FROM deck_cards AS d
                    INNER JOIN cards AS c ON c.name = d.card_name
                    WHERE d.deck_id = :deck_id
                    """
                ),
                [{"deck_id": deck_id}]
            ).all()
    
    value_sum = 0
    highest_value = 0
    lowest_value = 100
    for row in deck_contents:
        if row[1] > 100: #price
            card_value = 100
        else:
            card_value = row[1]
        
        if card_value > highest_value:
            highest_value = card_value
        if card_value < lowest_value:
            lowest_value = card_value
        value_sum += card_value
    
    avg_value = value_sum / len(deck_contents)

    win_prob = 0.01 * (30 + (avg_value * 0.4) + (highest_value * 0.2) + (lowest_value * 0.1))
    battle_result = np.random.choice(['Victory!', 'Defeat...'], [win_prob, 1-win_prob])

    if (battle_result == 'Victory!'):
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                """
                UPDATE users SET
                coins = coins + :prize
                WHERE id = :user_id
                """
                ),
                [{"prize": 100, #arbitrary prize money amount
                  "user_id": user_id}]
            )
    
    return battle_result
