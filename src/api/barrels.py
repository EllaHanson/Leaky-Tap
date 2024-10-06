from fastapi import APIRouter, Depends
from pydantic import BaseModel
from . import auth

#added for version 1
import sqlalchemy
from src import database as db
#import src
#till here


router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    price = 0
    delivered_ml = 0

    for n in barrels_delivered:
        price += (n.price * n.quantity)
        delivered_ml += (n.ml_per_barrel * n.quantity)

    print(delivered_ml)

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory set num_green_ml = num_green_ml + {delivered_ml}"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory set gold = gold - {price}"))

        #connection.execute(sqlalchemy.text(f"UPDATE global_inventory set num_green_ml = 0"))
        #connection.execute(sqlalchemy.text(f"UPDATE global_inventory set gold = 100"))

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        res_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).fetchone()
        green_potions = res_potions.num_green_potions
        res_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).fetchone()
        green_ml = res_ml.num_green_ml
        res_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).fetchone()
        gold_num = res_gold.gold
    
    in_stock = 0
    for x in wholesale_catalog:
        if x.sku == "SMALL_GREEN_BARREL":
            in_stock += 1
    
    if (in_stock >= 1) and (green_potions < 10) and (gold_num >= 100):
        return [{"sku": "SMALL_GREEN_BARREL","quantity": 1 }]
    else:
        return[]


    """
    #setting up prompt to get for how many green potion my shop has
    with db.engine.begin() as connection:
        green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar
        gold_num = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar

    if (in_stock >= 1) and (green_potions < 10) and (gold_num >= 100):
        return [{"sku": "SMALL_GREEN_BARREL","quantity": 1 }]
    else:
        return []
    """
    
    