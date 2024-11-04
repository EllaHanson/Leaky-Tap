from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

#added for version 1
import sqlalchemy
from src import database as db
#till here

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    #version 1
    print(f"potions delievered:")
    for n in potions_delivered:
        print(n)

    total_used_red = 0
    total_used_green = 0
    total_used_blue = 0
    total_used_dark = 0
    potions_add = []

    with db.engine.begin() as connection:
        result_potion_options = connection.execute(sqlalchemy.text("SELECT id, sku, name, red, green, blue, dark, price FROM potion_option ORDER BY id")).fetchall()
        result_potion_amount = connection.execute(sqlalchemy.text("SELECT potion_id, SUM(amount) as amount FROM potion_log GROUP BY potion_id HAVING SUM(amount) > 0")).fetchall()

    
        for n in result_potion_options:
            temp_id = n.id
            sku = n.sku
            name = n.name
            potion_option = [n.red, n.green, n.blue, n.dark]

            for x in potions_delivered:
                bottled_potion = [x.potion_type[0], x.potion_type[1], x.potion_type[2], x.potion_type[3]]
                if potion_option == bottled_potion:
                    print("-adding", name)
                    total_used_red += x.potion_type[0] * x.quantity
                    total_used_green += x.potion_type[1] * x.quantity
                    total_used_blue += x.potion_type[2] * x.quantity
                    total_used_dark += x.potion_type[3] * x.quantity
                    potions_add.append((x.quantity, temp_id))
     
    with db.engine.begin() as connection:
        print("total used ml: ", total_used_red, total_used_green, total_used_blue, total_used_dark)
        print("inserting ml entry...")
        connection.execute(sqlalchemy.text("INSERT INTO ml (red_diff, green_diff, blue_diff, dark_diff) VALUES (:red, :green, :blue, :dark)"), {"red": -total_used_red, "green": -total_used_green, "blue": -total_used_blue, "dark": -total_used_dark})
        print("inserting potion log...")
        for n in potions_add:
            connection.execute(sqlalchemy.text("INSERT INTO potion_log (potion_id, amount) VALUES (:id, :num)"), {"id": n[1], "num": n[0]})

    return "OK"


@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    with db.engine.begin() as connection:
        result_potion_options = connection.execute(sqlalchemy.text("SELECT * FROM potion_option ORDER BY id")).fetchall()
        result_ml_amount = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(red_diff), 0) AS red, COALESCE(SUM(green_diff), 0) AS green, COALESCE(SUM(blue_diff), 0) AS blue, COALESCE(SUM(dark_diff), 0) AS dark FROM ml")).fetchone()     
        potion_amount = connection.execute(sqlalchemy.text("SELECT potion_id, SUM(amount) as amount FROM potion_log GROUP BY potion_id HAVING SUM(amount) > 0")).fetchall()

        available_red = result_ml_amount.red
        available_green = result_ml_amount.green
        available_blue = result_ml_amount.blue
        available_dark = result_ml_amount.dark
        
        total_potion_num = 0
        for n in potion_amount:
            total_potion_num += n.amount

        print("available ml: ")
        print("  red -", available_red)
        print("  green -", available_green)
        print("  blue -", available_blue)
        print("  dark -", available_dark)

        return_list =[]

        total_made_potions = 0

        for n in result_potion_options:
            option_id = n.id
            required_red = n.red
            required_green = n.green
            required_blue = n.blue
            required_dark = n.dark

            count = 0
            potion_num = 0
            for x in potion_amount:
                if x.potion_id == option_id:
                    potion_num = x.amount
                    break

            while (potion_num + count < 10) and (total_made_potions + total_potion_num + count < 50) and (available_red >= required_red) and (available_green >= required_green) and (available_blue >= required_blue) and (available_dark >= required_dark):
                available_red -= required_red
                available_green -= required_green
                available_blue -= required_blue
                available_dark -= required_dark
                count += 1
            if count > 0:
                print(f"bottling {count} {n.sku} potion...")
                return_list.append({"potion_type": [required_red,required_green,required_blue,required_dark], "quantity": count})
                total_made_potions += count
            
        print("Bottle Transaction:")
        for n in return_list:
            print(n)
        return return_list

if __name__ == "__main__":
    print(get_bottle_plan())
