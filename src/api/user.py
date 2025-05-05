from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
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
    userid: int

class UserCreateResponse(BaseModel):
    user_id: int

@router.post("/users/register/", response_model=UserCreateResponse)
def register_user(new_user: User):
    """Register a user. If the user already exists, raise an exception.
    If the user does not exist, add them to the users_table and return the id."""

    with db.engine.begin() as conn:
        # Check if user already exists
        existing_user = conn.execute(
            sqlalchemy.text("SELECT User_id FROM users_table WHERE Username = :username"),
            {"username": new_user.username}
        ).fetchone()

        if existing_user:
            raise Exception("User already exists")

        # Insert new user with default Coins (e.g., 0)
        result = conn.execute(
            sqlalchemy.text("""
                INSERT INTO users_table (Username, Coins)
                VALUES (:username, :coins)
                RETURNING User_id
            """),
            {"username": new_user.username, "coins": 0}
        )
        user_id = result.scalar()

    return UserCreateResponse(user_id=user_id)


