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
    price = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    dark_ml = 0
    for n in barrels_delivered:
        print(n)
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
            result_ml = connection.execute(sqlalchemy.text(f"SELECT * FROM ml_log ORDER BY id DESC LIMIT 1")).fetchone()
            print("total used ml: ", red_ml, green_ml, blue_ml, dark_ml)
            entry_id = connection.execute(sqlalchemy.text(f"INSERT INTO ml_entry (red_diff, green_diff, blue_diff, dark_diff) VALUES ({red_ml}, {green_ml}, {blue_ml}, {dark_ml}) RETURNING entry_id")).fetchone()[0]
            print("inserting ml entry...")
            connection.execute(sqlalchemy.text(f"INSERT INTO ml_log (red, green, blue, dark, entry_id) VALUES ({result_ml[1]+red_ml}, {result_ml[2]+green_ml}, {result_ml[3]+blue_ml}, {result_ml[4]+dark_ml}, {entry_id})"))
            print("updating ml log...")
            gold = connection.execute(sqlalchemy.text(f"SELECT balance FROM gold ORDER BY id DESC LIMIT 1")).fetchone()[0]
            return_gold = connection.execute(sqlalchemy.text("INSERT INTO gold_entry (gold_diff) VALUES (:diff) RETURNING entry_id"), {"diff": -price})
            gold_id = return_gold.fetchone()[0]
            connection.execute(sqlalchemy.text("INSERT INTO gold (balance, entry_id) VALUES (:new_balance, :entry_id)"), {"new_balance": gold-price, "entry_id": gold_id})
            print("updating gold...")
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
        result_ml_amount = connection.execute(sqlalchemy.text(f"SELECT red, green, blue FROM ml_log ORDER BY id DESC LIMIT 1")).fetchone()     
        red_ml = result_ml_amount[0]
        green_ml = result_ml_amount[1]
        blue_ml = result_ml_amount[2]
        gold = connection.execute(sqlalchemy.text(f"SELECT balance FROM gold ORDER BY id DESC LIMIT 1")).fetchone()[0]
        return_list = []
        if gold < 100:
            return return_list
        
        if red_ml < 500:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_RED_BARREL":
                    in_stock += x.quantity  
            if (in_stock) and (gold >= 100):
                print("buying small red barrel")
                gold -= 100
                if gold > 540 and in_stock > 1:
                    print("buying small red barrel")
                    return_list.append({"sku": "SMALL_RED_BARREL","quantity": 2 })
                    gold -= 100
                else:
                    return_list.append({"sku": "SMALL_RED_BARREL","quantity": 1 })

        if green_ml < 500:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_GREEN_BARREL":
                    in_stock += x.quantity  
            if (in_stock) and (gold >= 100):
                print("buying small green barrel")
                gold -= 100
                if gold > 340 and in_stock > 1:
                    print("buying small green barrel")
                    return_list.append({"sku": "SMALL_GREEN_BARREL","quantity": 2 })
                    gold -= 100
                else:
                    return_list.append({"sku": "SMALL_GREEN_BARREL","quantity": 1 })

        if blue_ml < 500:
            in_stock = 0
            for x in wholesale_catalog:
                if x.sku == "SMALL_BLUE_BARREL":
                    in_stock += x.quantity  
            if (in_stock) and (gold >= 100):
                print("buying small blue barrel")
                gold -= 120
                if gold >= 240 and in_stock > 1:
                    print("buying small green barrel")
                    return_list.append({"sku": "SMALL_GREEN_BARREL","quantity": 2 })
                    gold -= 120
                else:
                    return_list.append({"sku": "SMALL_GREEN_BARREL","quantity": 1 })

        return return_list

    
    
    