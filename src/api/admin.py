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
        connection.execute(sqlalchemy.text("DELETE FROM ml"))
        connection.execute(sqlalchemy.text("DELETE FROM potion_log")) 
        connection.execute(sqlalchemy.text("DELETE from gold"))
        connection.execute(sqlalchemy.text("INSERT INTO gold (gold_diff) VALUES (100)"))
        connection.execute(sqlalchemy.text("DELETE FROM customers"))
        connection.execute(sqlalchemy.text("DELETE FROM cart_log"))
        connection.execute(sqlalchemy.text("DELETE FROM cart_entry"))

    return "OK"

