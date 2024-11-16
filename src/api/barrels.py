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
        connection.execute(sqlalchemy.text(f"INSERT INTO ml (red_diff, green_diff, blue_diff, dark_diff) VALUES ({red_ml}, {green_ml}, {blue_ml}, {dark_ml})"))

        print("inserting gold entry...")
        connection.execute(sqlalchemy.text("INSERT INTO gold (gold_diff) VALUES (:diff)"), {"diff": -price})

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
        result_ml_amount = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(red_diff),0) AS total_red, COALESCE(SUM(green_diff),0) AS total_green, COALESCE(SUM(blue_diff),0) AS total_blue FROM ml")).fetchone()     
        red_ml = result_ml_amount.total_red
        green_ml = result_ml_amount.total_green
        blue_ml = result_ml_amount.total_blue
        total_ml = red_ml + green_ml + blue_ml
        gold = connection.execute(sqlalchemy.text("SELECT COALESCE(sum(gold_diff),0) FROM gold")).fetchone()[0]
        capacity = connection.execute(sqlalchemy.text("SELECT type, COALESCE(sum(amount),0) as num FROM capacity WHERE type = 'ml' GROUP BY type")).fetchone()
        ml_cap = capacity.num + 10000

        return_list = [] 

        print (total_ml)
        
        if gold < 100:
            return return_list
        
        red_stock = 0
        green_stock = 0
        blue_stock = 0
        for x in wholesale_catalog:
            if x.sku == "SMALL_RED_BARREL":
                red_stock += x.quantity
            if x.sku == "SMALL_GREEN_BARREL":
                green_stock += x.quantity  
            if x.sku == "SMALL_BLUE_BARREL":
                blue_stock += x.quantity  
        
        red_count = 0
        green_count = 0
        blue_count = 0
        total_bought = 0

        while ((gold >= 100 and (red_stock or green_stock)) or (gold >= 120 and blue_stock)) and (total_ml + total_bought + 1500 < ml_cap):
            if (red_stock) and (gold >= 100):
                red_count += 1
                red_stock -= 1             
                gold -= 100
                total_bought += 500
            if (green_stock) and (gold >= 100):
                green_count += 1
                green_stock -= 1
                gold -= 100
                total_bought += 500
            if (blue_stock) and (gold >= 120):
                blue_count += 1
                blue_stock -= 1             
                gold -= 120
                total_bought += 500

        if (red_count):
            return_list.append({"sku": "SMALL_RED_BARREL","quantity": red_count})
        if (green_count):
            return_list.append({"sku": "SMALL_GREEN_BARREL","quantity": green_count})
        if (blue_count):
            return_list.append({"sku": "SMALL_BLUE_BARREL","quantity": blue_count})

        return return_list