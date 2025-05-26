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

def check_user_exists(user_id: int):
     with db.engine.begin() as connection:
        existing_user = connection.execute(sqlalchemy.text("""
            SELECT id FROM users WHERE id = :user_id
        """), {"user_id": user_id}).scalar_one_or_none()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User does not exist")
        else:
             return True
    
@router.get("/{user_id}/get/{type}", tags=["collection"], response_model = List[CollectionInfo])
def get_collection_by_type(user_id: int, type: str):
        check_user_exists(user_id)
        collection = []
        with db.engine.begin() as connection: 
            cards = connection.execute(sqlalchemy.text("""
                SELECT c.name, c.type, c.price, col.quantity FROM collection AS col
                LEFT JOIN cards AS c ON col.card_id = c.id
                WHERE col.user_id = :user_id AND c.type = :type
                                                    """),
                {"user_id": user_id, "type": type}
            ).all()
            for name, type, price, quantity in cards:
                collection.append(CollectionInfo(Card = Card(name=name, type=type, price=price), Quantity=quantity))
        return collection

@router.get("/{user_id}/get", tags=["collection"], response_model = List[CollectionInfo])
def get_full_collection(user_id: int):
        check_user_exists(user_id)
        collection = []
        with db.engine.begin() as connection: 
            cards = connection.execute(sqlalchemy.text("""
                SELECT c.name, c.type, c.price, col.quantity FROM collection AS col
                LEFT JOIN cards AS c ON col.card_id = c.id
                WHERE col.user_id = :user_id
                ORDER BY c.type
                                                    """),
                {"user_id": user_id}
            ).all()
            for name, type, price, quantity in cards:
                collection.append(CollectionInfo(Card = Card(name=name, type=type, price=price), Quantity=quantity))
        return collection


