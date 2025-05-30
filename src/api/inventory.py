from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

def check_user_exists(user_id: int):
     with db.engine.begin() as connection:
        existing_user = connection.execute(sqlalchemy.text("""
            SELECT id FROM users WHERE id = :user_id
        """), {"user_id": user_id}).scalar_one_or_none()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User does not exist")

class Pack(BaseModel):
    name: str
    price: int
    
class PackWithQuantity(BaseModel):
    pack: Pack
    quantity: int

class InventoryAudit(BaseModel):
    coins: int
    packs: List[PackWithQuantity]

@router.get("/user/{user_id}/audit", tags=["inventory"], response_model=InventoryAudit)
def get_inventory(user_id: int) -> InventoryAudit:
    """Returns all unopened packs and coins a user owns"""
    with db.engine.begin() as connection:
        # Check user exists
        check_user_exists(user_id)

        # Get user's coin balance
        coins = connection.execute(
            sqlalchemy.text("SELECT coins FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).scalar()

        # Get unopened packs
        owned_packs = connection.execute(
            sqlalchemy.text("""
                SELECT p.name AS name, p.price AS price, i.quantity AS quantity
                FROM inventory AS i
                JOIN packs AS p ON p.id = i.pack_id
                WHERE i.user_id = :user_id AND i.quantity > 0
            """),
            {"user_id": user_id}
        ).mappings()

        pack_inventory = [
            PackWithQuantity(pack=Pack(name=row["name"], price=row["price"]), quantity=row["quantity"])
            for row in owned_packs
        ]

    return InventoryAudit(coins=coins, packs=pack_inventory)
