from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db
from src.api.catalog import Pack

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

class InventoryAudit(BaseModel):
    packs: dict[Pack, int]
    #dict mapping each pack to the quantity owned by the user

@router.get("/audit", tags=["inventory"], response_model=InventoryAudit)
def get_inventory(user_id: int) -> InventoryAudit:
    """Returns a list of all unopened packs a user owns in their inventory given a specific user ID"""
    with db.engine.begin() as connection:
        owned_packs = connection.execute(
            sqlalchemy.text( # p.price may be renamed to p.price?
                """
                SELECT p.name, p.price, i.quantity FROM inventory as i
                INNER JOIN packs AS p ON p.id = i.pack_id
                WHERE user_id = :user_id
                """
            ),
            [{"user_id": user_id}],
        )
    
    pack_inventory = {}
    for pack_data in owned_packs:
        pack_inventory.update({Pack(name=pack_data[0], price=pack_data[1]):pack_data[2]})
    
    return InventoryAudit(packs=pack_inventory)
