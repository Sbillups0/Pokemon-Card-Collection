from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Annotated
import sqlalchemy
from src.api import auth
from src import database as db
from src.api.decks import create_deck
#Populates the table with 4 users, each with several cards and decks.
names_cards = [("Jessie",[16,17,18,19,20],["Slowpoke","Slowbro","Doduo","Dodrio","Gengar VMAX"]), 
               ("James",[21,22,23,24,25],["Grimer","Muk","Ghastly","Haunter","Gengar"]), 
               ("Ash",[36,37,38,39,40],["Lickitung","Lickilicky","Tangela","Tangrowth","Pikachu VMAX"]), 
               ("Misty",[45,46,49,50,51],["Staryu","Starmie","Porygon","Porygon2","Porygon-Z"])]


with db.engine.begin() as connection:
    for name, cards, temp in names_cards:
        id = connection.execute(sqlalchemy.text("INSERT INTO users(username, coins) VALUES(:username, 0) RETURNING id"),{"username": name}).scalar_one()
        for card in cards:
            connection.execute(sqlalchemy.text("INSERT INTO collection(user_id, card_id, quantity) VALUES(:id, :card_id, 1)"),{"id": id,"card_id": card})
        
with db.engine.begin() as connection:
    for name, cards, c_name in names_cards:
        id = connection.execute(sqlalchemy.text("SELECT id FROM users WHERE username = :username"),{"username": name}).scalar_one()
        create_deck(id, "Default_Deck", c_name)