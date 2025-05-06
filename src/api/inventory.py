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

class PackWithQuantity(BaseModel):
    pack: Pack
    quantity: int

class InventoryAudit(BaseModel):
    packs: List[PackWithQuantity]

@router.get("/{user_id}/audit", tags=["inventory"], response_model=InventoryAudit)
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
    
    pack_inventory = [
        PackWithQuantity(pack=Pack(name=row[0], price=row[1]), quantity=row[2])
        for row in owned_packs
    ]
    
    return InventoryAudit(packs=pack_inventory)
