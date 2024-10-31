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
    print("getting catalog...")

    #version 1
    with db.engine.begin() as connection:
        result_potion_option = connection.execute(sqlalchemy.text("SELECT id, sku, name, red, green, blue, dark, price FROM potion_option ORDER BY id")).fetchall()
        result_potion_amount = connection.execute(sqlalchemy.text("SELECT potion_id, SUM(amount) as amount FROM potion_log GROUP BY potion_id HAVING SUM(amount) > 0")).fetchall()

        return_list = []
        for n in result_potion_amount:
            amount = n.amount
            potion_option = result_potion_option[n.potion_id-1]
            potion_type = [potion_option.red, potion_option.green, potion_option.blue, potion_option.dark]
            return_list.append({"sku": potion_option.sku, "name": potion_option.name, "quantity": amount, "price": potion_option.price, "potion_type": potion_type})
            if len(return_list) == 6:
                for n in return_list:
                    print(n)
                return return_list
        
        for n in return_list:
            print(n)
        return return_list
