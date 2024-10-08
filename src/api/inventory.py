from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    print("performing audit")
    with db.engine.begin() as connection:
        potions_list = connection.execute(sqlalchemy.text("SELECT amount FROM potions")).fetchall()
        ml_list = connection.execute(sqlalchemy.text("SELECT amount FROM ml")).fetchall()
        res_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).fetchone()
        gold = res_gold.gold

        potion_count = 0
        ml_count = 0
        for n in potions_list:
            potion_count += n[0]
        for n in ml_list:
            ml_count += n[0]

        print("audit results:")
        print("potions: ", potion_count)
        print("ml: ", ml_count)
        print("gold: ", gold)

    
    return {"number_of_potions": potion_count, "ml_in_barrels": ml_count, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
