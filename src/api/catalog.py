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
        result_potion_option = connection.execute(sqlalchemy.text("SELECT * FROM potion_option ORDER BY id")).fetchall()
        result_potion_amount = connection.execute(sqlalchemy.text("SELECT * FROM potion_amount ORDER BY type_id")).fetchall()

        return_list = []
        for n in result_potion_amount:
            amount = n[2]
            if amount > 0:
                potion_option = result_potion_option[n[0]-1]
                #print(potion_option)
                potion_type = [potion_option[3], potion_option[4], potion_option[5], potion_option[6]]
                return_list.append({"sku": {potion_option[1]}, "name": {potion_option[2]}, "quantity": {amount}, "price": {potion_option[7]}, "potion_type": potion_type})
                if len(return_list) == 6:
                    for n in return_list:
                        print(n)
                    return return_list
        
        for n in return_list:
            print(n)
        return return_list
