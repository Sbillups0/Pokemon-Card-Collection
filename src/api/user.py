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
    

@router.post("/users/register/", response_model=List[User])
def register_user(wholesale_catalog: List[Pack]):
    """Returns a list of all booster packs available for purchase"""
    print(f"barrel catalog: {wholesale_catalog}")

