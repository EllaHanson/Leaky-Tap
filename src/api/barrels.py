from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

#added for version 1
import sqlalchemy
from src import database as db
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

    delivered_ml = len(barrels_delivered) * barrels_delivered[0].ml_per_barrel
    price = len(barrels_delivered) * barrels_delivered[0].price

    with db.engine.begin() as connection:
        update_ml = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = (num_green_ml + {delivered_ml})"))
        update_gold = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = (gold - {price})"))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    print("here plz")

    in_stock = 0
    for x in wholesale_catalog:
        if x.sku == "SMALL_GREEN_BARREL":
            in_stock = 1

    #setting up prompt to get for how many green potion my shop has
    
    with db.engine.begin() as connection:
        green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        gold_num = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()

        if green_potions is None: green_potions = 0
        if green_ml is None: green_ml = 0
        if gold_num is None: gold_num = 0

    if in_stock == 1 and green_potions < 10 and gold_num >= 100:
        return [{"sku": "SMALL_GREEN_BARREL","quantity": 1 }]
    else:
        return []

