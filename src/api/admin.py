from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    print("fully reseting tables...")
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE ml SET amount = 0"))
        connection.execute(sqlalchemy.text("UPDATE potions SET amount = 0"))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = 100"))
        connection.execute(sqlalchemy.text("DELETE FROM customers"))
        connection.execute(sqlalchemy.text("DELETE FROM carts"))

    return "OK"

