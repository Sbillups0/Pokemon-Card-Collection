from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db
# from src.api.packs import Pack  # Currently commented out, using local Pack model

router = APIRouter()

class Card(BaseModel):
    type: str
    name: str
    price: int

class Pack(BaseModel):
    name: str
    price: int

def create_catalog() -> List[Pack]:
    """
    Queries the database to retrieve the list of available packs,
    ordered by price descending and name ascending. Limits the catalog
    to a maximum of 6 items.

    Returns:
        List[Pack]: A list of Pack objects representing the catalog.
    """
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
        # Log to console for debugging purposes
        print("No packs found in the database to populate the catalog.")
        # Could alternatively raise an HTTPException if preferred:
        # raise HTTPException(status_code=404, detail="No packs available in the catalog.")
        return catalog_list

    # Limit the catalog size to 6 items
    for name, price in rows:
        if len(catalog_list) < 6:
            catalog_list.append(Pack(name=name, price=price))
        else:
            break

    return catalog_list

@router.get("/catalog/packs/", tags=["catalog"], response_model=List[Pack])
def get_catalog() -> List[Pack]:
    """
    Endpoint to retrieve the current catalog of packs available for purchase.
    
    Returns:
        List[Pack]: List of packs (up to 6), sorted by price descending then name ascending.
    """
    catalog = create_catalog()
    if not catalog:
        # Optional: raise 404 if no packs found
        # raise HTTPException(status_code=404, detail="No packs available in the catalog.")
        pass
    return catalog
