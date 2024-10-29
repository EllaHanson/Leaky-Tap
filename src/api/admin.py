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
        connection.execute(sqlalchemy.text("DELETE FROM ml_entry"))
        connection.execute(sqlalchemy.text("UPDATE balance SET gold = 100"))
        connection.execute(sqlalchemy.text("UPDATE ml SET red = 0, green = 0, blue = 0, dark = 0"))
        connection.execute(sqlalchemy.text("UPDATE potion_amount SET amount = 0")) 
        connection.execute(sqlalchemy.text("DELETE from gold_entry"))
        connection.execute(sqlalchemy.text("DELETE FROM customers"))
        connection.execute(sqlalchemy.text("DELETE FROM cart_log"))
        connection.execute(sqlalchemy.text("DELETE FROM cart_entry"))



    return "OK"

