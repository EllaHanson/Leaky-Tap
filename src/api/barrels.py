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
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {price} WHERE id = 1"))

    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print("--available barrels--")
    #print(wholesale_catalog)
    for n in wholesale_catalog:
        print(n)

    with db.engine.begin() as connection:
        potion_list = connection.execute(sqlalchemy.text("SELECT amount FROM potions")).scalars().all()
        ml_list = connection.execute(sqlalchemy.text("SELECT amount FROM ml")).scalars().all()

        #red potion info
        red_potions = potion_list[0]
        red_ml = ml_list[0]
        #green potion info
        green_potions = potion_list[1]
        green_ml = ml_list[1]
        #blue potion info
        blue_potions = potion_list[2]
        blue_ml = ml_list[2]
        #gold info
        res_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).fetchone()
        gold = res_gold.gold

        print("current potions,ml count: ")
        print(f"red: {potion_list[0]}, {ml_list[0]}")
        print(f"green: {potion_list[1]}, {ml_list[1]}")
        print(f"blue: {potion_list[2]}, {ml_list[2]}")
        
        print("Current gold:", gold)

        if gold < 100:
            return[]
    
        if red_potions <= 10 and red_ml < 100:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_RED_BARREL":
                    in_stock += 1  
            if (in_stock) and (gold >= 100):
                print("buying small red barrel")
                return [{"sku": "SMALL_RED_BARREL","quantity": 1 }]
            
        elif green_potions <= 10 and green_ml < 100:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_GREEN_BARREL":
                    in_stock += 1  
            if (in_stock) and (gold >= 100):
                print("buying small green barrel")
                return [{"sku": "SMALL_GREEN_BARREL","quantity": 1 }]
            
        elif blue_potions <= 10 and blue_ml < 100:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_BLUE_BARREL":
                    in_stock += 1  
            if (in_stock) and (gold >= 100):
                print("buying small blue barrel")
                return [{"sku": "SMALL_BLUE_BARREL","quantity": 1 }]
        

        return[]

    
    
    