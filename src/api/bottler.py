from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

#added for version 1
import sqlalchemy
from src import database as db
#till here

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    #version 1
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    
    used_ml = 0
    potions_made = 0
    for n in potions_delivered:
        used_ml += (n.quantity * 100)
        potions_made += n.quantity
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = (num_green_ml - {used_ml})"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = (num_green_potions + {potions_made})"))

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    #version 1
    with db.engine.begin() as connection:
        result_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).fetchone()
        green_ml = result_ml.num_green_ml
        result_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).fetchone()
        green_potion = result_green_potions.num_green_potions

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    if green_ml >= 100 and green_potion <= 10:
        potion_num = green_ml / 100
        return [{ "potion_type": [0, 100, 0, 0], "quantity": int(potion_num) }]
    else:
        return [] # return empty array for no bottling (??) i think

if __name__ == "__main__":
    print(get_bottle_plan())
