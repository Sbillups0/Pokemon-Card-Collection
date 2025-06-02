from dataclasses import dataclass
import time
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List
import sqlalchemy

from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

class User(BaseModel):
    username: str

class UserCreateResponse(BaseModel):
    user_id: int

class UserProfile(BaseModel):
    user_id: int
    username: str
    coins: int

@router.post("/register/", response_model=UserCreateResponse)
def register_user(username: str):
    """
    Register a new user.

    This endpoint creates a new user with the given username and assigns them a default of 100 coins.
    If a user with the same username already exists, it returns a 400 Bad Request error.

    Parameters:
    - username (str): The desired username for the new user.

    Returns:
    - UserCreateResponse: An object containing the new user's ID.
    """
    start_time = time.time()  # Start timer
    with db.engine.begin() as conn:
        # Check if user already exists
        existing_user = conn.execute(
            sqlalchemy.text("SELECT id FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"Registration failed: username '{username}' is already taken."
            )

        # Insert new user with default 100 coins
        result = conn.execute(
            sqlalchemy.text("""
                INSERT INTO users (username, coins)
                VALUES (:username, 100)
                RETURNING id
            """),
            {"username": username}
        )
        user_id = result.scalar()
    end_time = time.time()  # End timer
    elapsed_ms = (end_time - start_time) * 1000
    print(f"User registration for '{username}' completed in {elapsed_ms:.2f} ms")
    return UserCreateResponse(user_id=user_id)

@router.get("/profile/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: int):
    """
    Retrieve a user's profile.

    This endpoint fetches the username and coin balance for the user associated with the provided user ID.
    If the user ID does not exist, it returns a 404 Not Found error.

    Parameters:
    - user_id (int): The ID of the user whose profile is being requested.

    Returns:
    - UserProfile: An object containing the user's ID, username, and coin balance.
    """
    start_time = time.time()  # Start timer
    with db.engine.begin() as conn:
        user = conn.execute(
            sqlalchemy.text("""
                SELECT id, username, coins
                FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Profile retrieval failed: user with ID {user_id} not found."
            )
        end_time = time.time()  # End timer
        elapsed_ms = (end_time - start_time) * 1000
        print(f"User profile retrieval for ID {user_id} completed in {elapsed_ms:.2f} ms")
        return UserProfile(user_id=user.id, username=user.username, coins=user.coins)
