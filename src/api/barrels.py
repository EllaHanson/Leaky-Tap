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
    for n in barrels_delivered:
        print(n)

    price = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    dark_ml = 0

    for n in barrels_delivered:
        price += (n.price * n.quantity)
        if n.sku.find("RED") != -1:
            red_ml += (n.ml_per_barrel) * (n.quantity)
        elif n.sku.find("GREEN") != -1:
            green_ml += (n.ml_per_barrel) * (n.quantity)
        elif n.sku.find("BLUE") != -1:
            blue_ml += (n.ml_per_barrel) * (n.quantity)
        elif n.sku.find("DARK") != -1:
            dark_ml += (n.ml_per_barrel) * (n.quantity)
        else:
            print("error, idk what color barrel, thats not an option")

    print("ml bought:", red_ml, green_ml, blue_ml, dark_ml)

    with db.engine.begin() as connection:
        print("total used ml: ", red_ml, green_ml, blue_ml, dark_ml)

        print("inserting ml entry...")
        connection.execute(sqlalchemy.text(f"INSERT INTO ml_entry (red_diff, green_diff, blue_diff, dark_diff) VALUES ({red_ml}, {green_ml}, {blue_ml}, {dark_ml})"))
        print("updating ml log...")
        connection.execute(sqlalchemy.text("UPDATE ml SET red = red + :red_diff, green = green + :green_diff, blue = blue + :blue_diff, dark = dark + :dark_diff"), {"red_diff": red_ml , "green_diff": green_ml, "blue_diff": blue_ml, "dark_diff": dark_ml})

        print("updating gold...")
        connection.execute(sqlalchemy.text("UPDATE balance SET gold = gold - :gold_diff"), {"gold_diff": price})
        connection.execute(sqlalchemy.text("INSERT INTO gold_entry (gold_diff) VALUES (:diff)"), {"diff": -price})

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
        result_ml_amount = connection.execute(sqlalchemy.text(f"SELECT red, green, blue FROM ml WHERE id = 1")).fetchone()     
        red_ml = result_ml_amount.red
        green_ml = result_ml_amount.green
        blue_ml = result_ml_amount.blue
        gold = connection.execute(sqlalchemy.text(f"SELECT gold FROM balance WHERE id = 1")).fetchone()[0]
        return_list = [] 
        if gold < 100:
            return return_list
        
        if blue_ml < 500:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_BLUE_BARREL":
                    in_stock += x.quantity  
            if (in_stock > 1) and (gold >= 240):
                print("buying 2 small blue barrel")
                return_list.append({"sku": "SMALL_BLUE_BARREL","quantity": 2 })
                gold -= 240
            elif (in_stock) and (gold >= 120):
                print("buying 1 small blue barrel")
                return_list.append({"sku": "SMALL_BLUE_BARREL","quantity": 1 })
                gold -= 120
        
        if red_ml < 500:
            in_stock = 0
            # in_stock = amount of small red barrels in catalog
            for x in wholesale_catalog:
                if x.sku == "SMALL_RED_BARREL":
                    in_stock += x.quantity  
            if (in_stock > 1) and (gold >= 200):
                print("buying 2 small red barrel")
                return_list.append({"sku": "SMALL_RED_BARREL","quantity": 2 })
                gold -= 200
            elif (in_stock) and (gold >= 100):
                print("buying 1 small red barrel")
                return_list.append({"sku": "SMALL_RED_BARREL","quantity": 1 })
                gold -= 100


        if green_ml < 500:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_GREEN_BARREL":
                    in_stock += x.quantity  
            if (in_stock > 1) and (gold >= 200):
                print("buying 2 small green barrel")
                return_list.append({"sku": "SMALL_GREEN_BARREL","quantity": 2 })
                gold -= 200
            elif (in_stock) and (gold >= 100):
                print("buying 1 small green barrel")
                return_list.append({"sku": "SMALL_GREEN_BARREL","quantity": 1 })
                gold -= 100


        return return_list

    
    
    