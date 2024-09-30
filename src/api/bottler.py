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

    amount_potions = len(potions_delivered)
    green_ml_used = amount_potions * 100

    
    with db.engine.begin() as connection:
        updated_green_ml = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = (num_green_ml - {green_ml_used})"))
        updated_green_potions = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = (num_green_potions + {amount_potions})"))

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    #version 1
    with db.engine.begin() as connection:
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    if green_ml >= 500:
        return [
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": 5,
                }
            ]
    else:
        return [] # return empty array for no bottling (??) i think

if __name__ == "__main__":
    print(get_bottle_plan())
