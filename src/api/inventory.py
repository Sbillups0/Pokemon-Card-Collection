from fastapi import APIRouter, Depends, status, HTTPException
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
    """
    Verify that a user with the given user_id exists in the database.

    Raises:
        HTTPException (404): If no user with the specified ID is found.
    """
    with db.engine.begin() as connection:
        existing_user = connection.execute(
            sqlalchemy.text("SELECT id FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).scalar_one_or_none()

        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} does not exist."
            )

class Pack(BaseModel):
    name: str = Field(..., description="Name of the pack")
    price: int = Field(..., description="Price of the pack in coins")

class PackWithQuantity(BaseModel):
    pack: Pack = Field(..., description="Details of the pack")
    quantity: int = Field(..., description="Quantity of this pack owned by the user")

class InventoryAudit(BaseModel):
    coins: int = Field(..., description="User's current coin balance")
    packs: List[PackWithQuantity] = Field(..., description="List of unopened packs with quantities")

@router.get("/{user_id}/audit", tags=["inventory"], response_model=InventoryAudit)
def get_inventory(user_id: int) -> InventoryAudit:
    """
    Retrieve the inventory audit for a specified user.

    This includes the user's current coin balance and a list of all unopened packs 
    the user owns along with their quantities.

    Args:
        user_id (int): The ID of the user whose inventory is requested.

    Returns:
        InventoryAudit: An object containing the user's coins and unopened pack details.

    Raises:
        HTTPException (404): If the user with the given ID does not exist.
    """
    with db.engine.begin() as connection:
        # Validate that the user exists
        check_user_exists(user_id)

        # Fetch user's coin balance
        coins = connection.execute(
            sqlalchemy.text("SELECT coins FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).scalar()

        # Fetch unopened packs owned by the user with quantity > 0
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
            PackWithQuantity(
                pack=Pack(name=row["name"], price=row["price"]),
                quantity=row["quantity"]
            )
            for row in owned_packs
        ]

    return InventoryAudit(coins=coins, packs=pack_inventory)
