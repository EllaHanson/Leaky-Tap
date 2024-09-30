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
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        """

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    #version 1
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": 5,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
