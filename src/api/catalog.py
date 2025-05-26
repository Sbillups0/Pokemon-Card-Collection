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
    price: int


class Pack(BaseModel):
    name: str
    price: int
    

# Placeholder function, you will replace this with a database call
def create_catalog() -> List[Pack]:
    catalog_list = []
    with db.engine.begin() as connection:
        rows = connection.execute(
            sqlalchemy.text(
                """
                SELECT name, price
                FROM packs
                ORDER BY price DESC, name ASC
                """
            )
        ).all()

    if not rows:
        print("No packs found in the database to populate the catalog.")
        return catalog_list

    # Limit catalog to max 6 items
    for name, price in rows:
        if len(catalog_list) < 6:
            catalog_list.append(Pack(name=name, price=price))
        else:
            break

    return catalog_list


@router.get("/packs/catalog/", tags=["catalog"], response_model=List[Pack])
def get_catalog() -> List[Pack]:
    """
    Retrieves the catalog of five packs that are available to purchase.
    """
    return create_catalog()
