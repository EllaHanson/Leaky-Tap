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
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).fetchone()
        green_potions = result.num_green_potions
    

    return [
            {"sku": "GREEN_POTION", "name": "green potion", "quantity": green_potions, "price": 50, "potion_type": [0, 100, 0, 0],}
        ]
