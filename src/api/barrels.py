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
    print("--buying barrels--")
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    price = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0

    for n in barrels_delivered:
        price += (n.price * n.quantity)
        if n.sku.find("RED") != -1:
            red_ml += (n.ml_per_barrel) * (n.quantity)
        elif n.sku.find("GREEN") != -1:
            green_ml += (n.ml_per_barrel) * (n.quantity)
        elif n.sku.find("BLUE") != -1:
            blue_ml += (n.ml_per_barrel) * (n.quantity)
        else:
            print("error, idk what color barrel, thats not an option")

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE ml SET amount = amount + {red_ml} WHERE color = 'red'"))
        connection.execute(sqlalchemy.text(f"UPDATE ml SET amount = amount + {green_ml} WHERE color = 'green'"))
        connection.execute(sqlalchemy.text(f"UPDATE ml SET amount = amount + {blue_ml} WHERE color = 'blue'"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory set gold = gold - {price}"))

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print("--available barrels")
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        #red potion info
        result_red_potions = connection.execute(sqlalchemy.text("SELECT amount FROM potions WHERE color = 'red'")).fetchone()
        red_potions = result_red_potions.amount
        result_red_ml = connection.execute(sqlalchemy.text("SELECT amount FROM ml WHERE color = 'red'")).fetchone()
        red_ml = result_red_ml.amount
        #green potion info
        result_green_potions = connection.execute(sqlalchemy.text("SELECT amount FROM potions WHERE color = 'green'")).fetchone()
        green_potions = result_green_potions.amount
        result_green_ml = connection.execute(sqlalchemy.text("SELECT amount FROM ml WHERE color = 'green'")).fetchone()
        green_ml = result_green_ml.amount
        #blue potion info
        result_blue_potions = connection.execute(sqlalchemy.text("SELECT amount FROM potions WHERE color = 'blue'")).fetchone()
        blue_potions = result_blue_potions.amount
        result_blue_ml = connection.execute(sqlalchemy.text("SELECT amount FROM ml WHERE color = 'blue'")).fetchone()
        blue_ml = result_blue_ml.amount
        #gold info
        res_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).fetchone()
        gold = res_gold.gold

        if gold < 100:
            return[]
    
        if red_potions <= 10 and red_ml < 100:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_RED_BARREL":
                    in_stock += 1  
            if (in_stock) and (gold >= 100):
                return [{"sku": "SMALL_RED_BARREL","quantity": 1 }]
            
        elif green_potions <= 10 and green_ml < 100:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_GREEN_BARREL":
                    in_stock += 1  
            if (in_stock) and (gold >= 100):
                return [{"sku": "SMALL_GREEN_BARREL","quantity": 1 }]
            
        elif blue_potions <= 10 and blue_ml < 100:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_BLUE_BARREL":
                    in_stock += 1  
            if (in_stock) and (gold >= 100):
                return [{"sku": "SMALL_BLUE_BARREL","quantity": 1 }]
        
        return[]

    
    
    