from fastapi import APIRouter

#added for version 1
import sqlalchemy
from src import database as db
#till here

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    #version 1
    with db.engine.begin() as connection:
        result_red_potions = connection.execute(sqlalchemy.text("SELECT amount FROM potions WHERE color = 'red'")).fetchone()
        red_potions = result_red_potions.amount
        result_green_potions = connection.execute(sqlalchemy.text("SELECT amount FROM potions WHERE color = 'green'")).fetchone()
        green_potions = result_green_potions.amount
        result_blue_potions = connection.execute(sqlalchemy.text("SELECT amount FROM potions WHERE color = 'blue'")).fetchone()
        blue_potions = result_blue_potions.amount

    

    return [
            {"sku": "RED_POTION", "name": "red potion", "quantity": red_potions, "price": 50, "potion_type": [0, 100, 0, 0]},
            {"sku": "GREEN_POTION", "name": "green potion", "quantity": green_potions, "price": 50, "potion_type": [0, 100, 0, 0]},
            {"sku": "BLUE_POTION", "name": "blue potion", "quantity": blue_potions, "price": 50, "potion_type": [0, 0, 100, 0]}
        ]
