from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Annotated
import sqlalchemy
from src.api import auth
from src import database as db
#from src.api.packs import Pack

router = APIRouter()

class Card(BaseModel):
    type: str
    name: str


class Pack(BaseModel):
    name: str
    price: int
    """possible_cards: List[Card] = Field(
        ...,
        min_length=30,
        max_length=30,
        description="Must contain 30 cards",
    )"""


# Placeholder function, you will replace this with a database call
def create_catalog() -> List[Pack]:
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT name, price FROM packs
                """
            )
        ).all()
    catalog_list = []
    #Loop through every pack in the database and add it to the catalog_list
    for name, price in row:
        if(len(catalog_list)<5):
            catalog_list += [Pack(name=name, price=price)]
        else:
            #If catalog_list is full (Has 6 items) loop ends
            break


    return catalog_list


@router.get("/catalog/", tags=["catalog"], response_model=List[Pack])
def get_catalog() -> List[Pack]:
    """
    Retrieves the catalog of items. Each unique item combination should have only a single price.
    You can have at most 6 potion SKUs offered in your catalog at one time.
    """
    return create_catalog()