from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Annotated
import sqlalchemy
from src.api import auth
from src import database as db

with db.engine.begin() as connection:
    connection.execute(sqlalchemy.text("DELETE FROM deck_cards"))
    connection.execute(sqlalchemy.text("DELETE FROM decks"))
    connection.execute(sqlalchemy.text("DELETE FROM collection"))
    connection.execute(sqlalchemy.text("DELETE FROM inventory"))
    connection.execute(sqlalchemy.text("DELETE FROM users"))
    print("Reset Successful")