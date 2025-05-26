from dataclasses import dataclass
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

@router.post("/users/register/", response_model=UserCreateResponse)
def register_user(username: str):
    """Register a user. If the user already exists, raise an exception.
    If the user does not exist, add them to the users_table and return the id."""

    with db.engine.begin() as conn:
        # Check if user already exists
        existing_user = conn.execute(
            sqlalchemy.text("SELECT id FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Insert new user with default Coins (e.g., 0) pass in Name return the id used
        result = conn.execute(
            sqlalchemy.text("""
                INSERT INTO users (username, coins)
                VALUES (:username, 100)
                RETURNING id
            """),
            {"username": username}
        )
        user_id = result.scalar()

    return UserCreateResponse(user_id=user_id)


