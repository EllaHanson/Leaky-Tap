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

    with db.engine.begin() as connection:
        result_potion_options = connection.execute(sqlalchemy.text("SELECT * FROM potion_option")).fetchall()
        total_used_red = 0
        total_used_green = 0
        total_used_blue = 0
        total_used_dark = 0
    
        for n in result_potion_options:
            #print(n)
            temp_id = n[0]
            sku = n[1]
            name = n[2]
            required_red = n[3]
            required_green = n[4]
            required_blue = n[5]
            required_dark = n[6]
            potion_option = [required_red, required_green, required_blue, required_dark]
            #print(potion_option)
            for x in potions_delivered:
                bottled_potion = [x.potion_type[0], x.potion_type[1], x.potion_type[2], x.potion_type[3]]
                if potion_option == bottled_potion:
                    print("-adding", name)
                    total_used_red += x.potion_type[0]
                    total_used_green += x.potion_type[1]
                    total_used_blue += x.potion_type[2]
                    total_used_dark += x.potion_type[3]
                    #print(potion_option)
                    #print(bottled_potion)
                    connection.execute(sqlalchemy.text(f"UPDATE potion_amount SET amount = (amount + {x.quantity}) WHERE type_id = {temp_id}"))

        result_ml = connection.execute(sqlalchemy.text(f"SELECT * FROM ml_log ORDER BY id DESC LIMIT 1")).fetchone()
        print("total used ml: ", total_used_red, total_used_green, total_used_blue, total_used_dark)
        entry_id = connection.execute(sqlalchemy.text(f"INSERT INTO ml_entry (red_diff, green_diff, blue_diff, dark_diff) VALUES ({-total_used_red}, {-total_used_green}, {-total_used_blue}, {-total_used_dark}) RETURNING entry_id")).fetchone()
        print("inserting ml entry...")
        connection.execute(sqlalchemy.text(f"INSERT INTO ml_log (red, green, blue, dark, entry_id) VALUES ({result_ml[1]-total_used_red}, {result_ml[2]-total_used_green}, {result_ml[3]-total_used_blue}, {result_ml[4]-total_used_dark}, {entry_id[0]})"))
        print("updating ml log...")
        return "OK"


@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    with db.engine.begin() as connection:
        result_potion_options = connection.execute(sqlalchemy.text("SELECT * FROM potion_option")).fetchall()
        result_ml_amount = connection.execute(sqlalchemy.text(f"SELECT * FROM ml_log ORDER BY id DESC LIMIT 1")).fetchone()     
        print(result_ml_amount)
    
        available_red = result_ml_amount[1]
        available_green = result_ml_amount[2]
        available_blue = result_ml_amount[3]
        available_dark = result_ml_amount[4]

        print(available_red, available_green, available_blue, available_dark)
        
        return_list =[]
        for n in result_potion_options:
            #print(n)
            required_red = n[3]
            required_green = n[4]
            required_blue = n[5]
            required_dark = n[6]

            if (available_red >= required_red) and (available_green >= required_green) and (available_blue >= required_blue) and (available_dark >= required_dark):
                print(f"bottling {n[2]} potion...")
                return_list.append({"potion_type": [required_red,required_green,required_blue,required_dark], "quantity": 1})

        print("Bottle Transaction:")
        for n in return_list:
            print(n)
        return return_list

if __name__ == "__main__":
    print(get_bottle_plan())
