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

    #version 1
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
    """

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    #setting up prompt to get for how many green potion my shop has
    #version 1
    
    with db.engine.begin() as connection:
        green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    if green_potions < 10:
        print ("buy green ml")
        return [{"sku": "SMALL_GREEN_BARREL",
                  "quantity": "1" }]

    return [
        {
            "sku": "",
            "quantity": 0,
        }
    ]

