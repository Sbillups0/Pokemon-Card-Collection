from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
from fastapi import HTTPException

import sqlalchemy
from src.api import auth
from src import database as db
from src.api.catalog import Card


router = APIRouter(
    prefix="/collection",
    tags=["collection"],
    dependencies=[Depends(auth.get_api_key)],
)

class CollectionInfo(BaseModel):
    Card: Card
    Quantity: int

class CollectionResponse(BaseModel):
    Cards: List[CollectionInfo]
    TotalValue: float


def check_user_exists(user_id: int):
     with db.engine.begin() as connection:
        existing_user = connection.execute(sqlalchemy.text("""
            SELECT id FROM users WHERE id = :user_id
        """), {"user_id": user_id}).scalar_one_or_none()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User does not exist")
        else:
             return True
    
@router.get("/{user_id}/{type}", tags=["collection"], response_model = CollectionResponse)
def get_collection_by_type(user_id: int, type: str):
    check_user_exists(user_id)
    type = type.strip()
    total_value = 0.0
   
    collection = []
    with db.engine.begin() as connection: 
         # Inline query to get valid card types
        valid_types = set(connection.execute(
            sqlalchemy.text("SELECT DISTINCT type FROM cards")
        ).scalars().all())

        if type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid card type '{type}'. Valid types: {', '.join(valid_types)}"
            )
        cards = connection.execute(sqlalchemy.text("""
            SELECT c.name, c.type, c.price, col.quantity FROM collection AS col
            LEFT JOIN cards AS c ON col.card_id = c.id
            WHERE col.user_id = :user_id AND LOWER(c.type) = LOWER(:type)
                                                """),
            {"user_id": user_id, "type": type}
        ).all()
        for name, ctype, price, quantity in cards:
            collection.append(CollectionInfo(Card = Card(name=name, type=ctype, price=price), Quantity=quantity))
            total_value += price * quantity
    return CollectionResponse(Cards=collection, TotalValue=total_value)

@router.get("/{user_id}", tags=["collection"], response_model = CollectionResponse)
def get_full_collection(user_id: int):
    check_user_exists(user_id)
    collection = []
    total_value = 0.0
    with db.engine.begin() as connection: 
        cards = connection.execute(sqlalchemy.text("""
            SELECT c.name, c.type, c.price, col.quantity FROM collection AS col
            LEFT JOIN cards AS c ON col.card_id = c.id
            WHERE col.user_id = :user_id
            ORDER BY c.type
                                                """),
            {"user_id": user_id}
        ).all()
        for name, ctype, price, quantity in cards:
            collection.append(CollectionInfo(Card = Card(name=name, type=ctype, price=price), Quantity=quantity))
            total_value += price * quantity
    return CollectionResponse(Cards=collection, TotalValue=total_value)


@router.get("/types", tags=["collection"])
def get_card_types():
    """Return all distinct card types."""
    with db.engine.begin() as connection:
        types = connection.execute(sqlalchemy.text("""
            SELECT DISTINCT type FROM cards
        """)).scalars().all()
        
    return {"types": types}

@router.get("/{user_id}/value", tags=["collection"])
def get_total_collection_value(user_id: int):
    """Return the total estimated value of a user's card collection."""
    check_user_exists(user_id)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT SUM(c.price * col.quantity) as total_value
            FROM collection AS col
            LEFT JOIN cards AS c ON col.card_id = c.id
            WHERE col.user_id = :user_id
        """), {"user_id": user_id}).scalar()

    return {"user_id": user_id, "total_value": result or 0.0}



