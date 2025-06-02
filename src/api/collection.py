from dataclasses import dataclass
import time
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List
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
    """
    Check if a user with the given user_id exists in the database.

    Args:
        user_id (int): The ID of the user to check.

    Raises:
        HTTPException 404: If the user does not exist.

    Returns:
        bool: True if user exists.
    """
    with db.engine.begin() as connection:
        existing_user = connection.execute(
            sqlalchemy.text("SELECT id FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).scalar_one_or_none()
        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} does not exist."
            )
        else:
            return True
@router.get("/types", tags=["collection"])
def get_card_types():
    """
    Retrieve all distinct card types available in the catalog.

    Returns:
        dict: Dictionary containing a list of distinct card types under the key "types".
    """
    start_time = time.time()  # Start timer
    with db.engine.begin() as connection:
        types = connection.execute(
            sqlalchemy.text("SELECT DISTINCT type FROM cards")
        ).scalars().all()
    end_time = time.time()  # End timer
    elapsed_ms = (end_time - start_time) * 1000
    print(f"Completed in {elapsed_ms:.2f} ms")
    return {"types": types}

@router.get("/{user_id}/value", tags=["collection"])
def get_total_collection_value(user_id: int):
    """
    Calculate the total estimated monetary value of a user's entire card collection.

    Args:
        user_id (int): The ID of the user.

    Raises:
        HTTPException 404: If the user does not exist.

    Returns:
        dict: Dictionary with 'user_id' and 'total_value' keys.
    """
    start_time = time.time()  # Start timer
    check_user_exists(user_id)

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                SELECT SUM(c.price * col.quantity) as total_value
                FROM collection AS col
                LEFT JOIN cards AS c ON col.card_id = c.id
                WHERE col.user_id = :user_id
            """),
            {"user_id": user_id}
        ).scalar()
    end_time = time.time()  # End timer
    elapsed_ms = (end_time - start_time) * 1000
    print(f"Completed in {elapsed_ms:.2f} ms")
    return {"user_id": user_id, "total_value": result or 0.0}

@router.get("/{user_id}/{type}", tags=["collection"], response_model=CollectionResponse)
def get_collection_by_type(user_id: int, type: str):
    """
    Retrieve all cards of a specific type from a user's collection.

    Args:
        user_id (int): The ID of the user.
        type (str): The type of cards to retrieve.

    Raises:
        HTTPException 400: If the card type is invalid.
        HTTPException 404: If the user does not exist.

    Returns:
        CollectionResponse: Contains a list of cards and total value of the selected type.
    """
    start_time = time.time()  # Start timer
    check_user_exists(user_id)
    type = type.strip()
    total_value = 0.0
    collection = []

    with db.engine.begin() as connection:
        # Fetch all valid card types
        valid_types = set(connection.execute(
            sqlalchemy.text("SELECT DISTINCT type FROM cards")
        ).scalars().all())

        if type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid card type '{type}'. Valid types are: {', '.join(sorted(valid_types))}."
            )

        cards = connection.execute(
            sqlalchemy.text("""
                SELECT c.name, c.type, c.price, col.quantity FROM collection AS col
                LEFT JOIN cards AS c ON col.card_id = c.id
                WHERE col.user_id = :user_id AND LOWER(c.type) = LOWER(:type)
            """),
            {"user_id": user_id, "type": type}
        ).all()

        for name, ctype, price, quantity in cards:
            collection.append(CollectionInfo(Card=Card(name=name, type=ctype, price=price), Quantity=quantity))
            total_value += price * quantity
    end_time = time.time()  # End timer
    elapsed_ms = (end_time - start_time) * 1000
    print(f"Completed in {elapsed_ms:.2f} ms")
    return CollectionResponse(Cards=collection, TotalValue=total_value)

@router.get("/{user_id}", tags=["collection"], response_model=CollectionResponse)
def get_full_collection(user_id: int):
    """
    Retrieve the full card collection for a user.

    Args:
        user_id (int): The ID of the user.

    Raises:
        HTTPException 404: If the user does not exist.

    Returns:
        CollectionResponse: Contains the full list of cards and their total value.
    """
    start_time = time.time()  # Start timer
    check_user_exists(user_id)
    collection = []
    total_value = 0.0

    with db.engine.begin() as connection:
        cards = connection.execute(
            sqlalchemy.text("""
                SELECT c.name, c.type, c.price, col.quantity FROM collection AS col
                LEFT JOIN cards AS c ON col.card_id = c.id
                WHERE col.user_id = :user_id
                ORDER BY c.type
            """),
            {"user_id": user_id}
        ).all()

        for name, ctype, price, quantity in cards:
            collection.append(CollectionInfo(Card=Card(name=name, type=ctype, price=price), Quantity=quantity))
            total_value += price * quantity
    end_time = time.time()  # End timer
    elapsed_ms = (end_time - start_time) * 1000
    print(f"Completed in {elapsed_ms:.2f} ms")
    return CollectionResponse(Cards=collection, TotalValue=total_value)

