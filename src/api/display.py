from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
from fastapi import HTTPException

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

@router.post("/{user_id}/get/{type}", tags=["display"], status_code=status.HTTP_204_NO_CONTENT)
def add_to_display(user_id: int, card_name: str):
    check_user_exists(user_id)
    with db.engine.begin() as connection:
        in_collection = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT * FROM collection as co 
                    INNER JOIN cards as ca ON co.card_id = ca.id
                    WHERE ca.name = :card_name
                    """
                ),
                [{"card_name": card_name}]
            ).all()
        current_display = [row.card_name for row in connection.execute(
                sqlalchemy.text(
                    """
                    SELECT c.card_name FROM cards as c 
                    INNER JOIN display as d ON d.card_id = c.id
                    WHERE d.user_id = :user_id
                    """
                ),
                [{"user_id": user_id}]
            ).all()]
    
    if len(in_collection) == 0:
        raise HTTPException(status_code=404, detail="Card not in user's collection")
    elif len(current_display) == 4:
        raise HTTPException(status_code=403, detail="User's display is full")
    elif card_name in current_display:
        raise HTTPException(status_code=403, detail="Card is already in user's display")
    
    card_id = in_collection[0]['card_id']
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
            """
            INSERT INTO display VALUES (:user_id, :card_id)
            """
            ),
            [{"user_id": user_id,
              "card_id": card_id}]
        )
    
    