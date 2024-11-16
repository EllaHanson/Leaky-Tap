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
    with db.engine.begin() as connection:
        print("performing audit...")
        potion_count = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(amount), 0) as amount FROM potion_log")).fetchone()[0]
        ml = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(red_diff), 0) AS red, COALESCE(SUM(green_diff), 0) AS green, COALESCE(SUM(blue_diff), 0) AS blue, COALESCE(SUM(dark_diff), 0) AS dark FROM ml")).fetchone()     
        gold = connection.execute(sqlalchemy.text("SELECT sum(gold_diff) FROM gold")).fetchone()[0]
        ml_count = ml.red + ml.green + ml.blue + ml.dark

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
    with db.engine.begin() as connection:
        potion_count = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(amount), 0) as amount FROM potion_log")).fetchone()[0]
        ml = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(red_diff), 0) AS red, COALESCE(SUM(green_diff), 0) AS green, COALESCE(SUM(blue_diff), 0) AS blue, COALESCE(SUM(dark_diff), 0) AS dark FROM ml")).fetchone()     
        gold = connection.execute(sqlalchemy.text("SELECT sum(gold_diff) FROM gold")).fetchone()[0]
        curr_potion_cap = connection.execute(sqlalchemy.text("SELECT sum(amount) AS num FROM capacity WHERE type = 'potion'  GROUP BY type")).fetchone().num + 25
        curr_ml_cap = connection.execute(sqlalchemy.text("SELECT sum(amount) AS num FROM capacity WHERE type = 'ml' GROUP BY type")).fetchone().num + 5000
        ml_count = ml.red + ml.green + ml.blue + ml.dark

        potion_capacity = 0
        ml_capacity = 0

        if potion_count > curr_potion_cap and gold > 1000:
            potion_capacity = 1
        if ml_count > curr_ml_cap and gold > 1000:
            ml_capacity = 1

    return {
        "potion_capacity": potion_capacity,
        "ml_capacity": ml_capacity
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
    with db.engine.begin() as connection:
        if capacity_purchase.potion_capacity > 0:
            connection.execute(sqlalchemy.text("INSERT INTO capacity (type, amount) VALUES ('potion', :temp_amount)"), {"temp_amount": (50 * capacity_purchase.potion_capacity)})
        if capacity_purchase.ml_capacity > 0:
            connection.execute(sqlalchemy.text("INSERT INTO capacity (type, amount) VALUES ('ml', :temp_amount)"), {"temp_amount": (10000 * capacity_purchase.ml_capacity)})
        
        price = 0
        price += (capacity_purchase.ml_capacity * 1000)
        price += (capacity_purchase.potion_capacity * 1000)
        if price > 0:
            connection.execute(sqlalchemy.text("INSERT INTO gold (gold_diff) VALUES (:diff)"), {"diff": -price})

    return "OK"
