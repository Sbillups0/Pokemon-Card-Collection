from dataclasses import dataclass
import time
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List
import sqlalchemy

from src.api import auth
from src import database as db
from src.api.catalog import Card
from src.api.collection import check_user_exists

router = APIRouter(
    prefix="/display",
    tags=["display"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/{user_id}/{card_name}", tags=["display"], status_code=status.HTTP_204_NO_CONTENT)
def add_to_display(user_id: int, card_name: str):
    """
    Add a card to a user's display, if possible.

    The card must exist in the user's collection. The user's display can hold a maximum of 4 cards,
    and the same card cannot be added multiple times.

    Args:
        user_id (int): The ID of the user.
        card_name (str): The name of the card to add to the display.

    Raises:
        HTTPException 404: If the card is not found in the user's collection.
        HTTPException 403: If the user's display already contains 4 cards.
        HTTPException 403: If the card is already present in the user's display.
    """
    start_time = time.time()  # Start timer
    # Verify the user exists
    check_user_exists(user_id)

    with db.engine.begin() as connection:
        # Check if the card is in user's collection
        in_collection = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM collection AS co 
                INNER JOIN cards AS ca ON co.card_id = ca.id
                WHERE ca.name = :card_name AND co.user_id = :user_id
                """
            ),
            {"card_name": card_name, "user_id": user_id}
        ).all()

        # Retrieve the current cards in user's display
        current_display = [
            row[0] for row in connection.execute(
                sqlalchemy.text(
                    """
                    SELECT c.name FROM cards AS c 
                    INNER JOIN display AS d ON d.card_id = c.id
                    WHERE d.user_id = :user_id
                    """
                ),
                {"user_id": user_id}
            ).all()
        ]

    # Validate presence of the card in the collection
    if len(in_collection) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Card '{card_name}' is not present in user {user_id}'s collection."
        )

    # Check if display is full
    if len(current_display) >= 4:
        raise HTTPException(
            status_code=403,
            detail=f"User {user_id}'s display is full (maximum 4 cards allowed)."
        )

    # Check if card already in display
    if card_name in current_display:
        raise HTTPException(
            status_code=403,
            detail=f"Card '{card_name}' is already in user {user_id}'s display."
        )

    # Get card_id from collection query result
    card_id = in_collection[0][1]

    # Insert the card into the user's display
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO display (user_id, card_id) VALUES (:user_id, :card_id)
                """
            ),
            {"user_id": user_id, "card_id": card_id}
        )
    end_time = time.time()  # End timer
    elapsed_ms = (end_time - start_time) * 1000
    print(f"Completed in {elapsed_ms:.2f} ms")
