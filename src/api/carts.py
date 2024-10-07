from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

#added for version 1
import sqlalchemy
from src import database as db
#till here

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    
    print("Which customers visited the shop today?")
    print(customers)

    
    with db.engine.begin() as connection:
        for n in customers:
            #check if this customer has been here before
            result_prev_customer = connection.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM customers WHERE name = '{n.customer_name}'")).fetchone()
            is_prev_customer = result_prev_customer.count

            if is_prev_customer:
                print(f"{n.customer_name} already in customer table")
            else:
                print(f"adding {n.customer_name} to customer table...")
                connection.execute(sqlalchemy.text(f"INSERT INTO customers (name,class,level) VALUES ('{n.customer_name}','{n.character_class}',{n.level})" ))
                
    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    #version 1
    with db.engine.begin() as connection:
        customer_name = new_cart.customer_name
        result_customer = connection.execute(sqlalchemy.text(f"SELECT customer_id FROM customers WHERE name = '{customer_name}'")).fetchone()
        temp_customer_id = result_customer.customer_id

        connection.execute(sqlalchemy.text(f"INSERT INTO carts (customer_id) VALUES ({temp_customer_id})" ))
        result_temp_id = connection.execute(sqlalchemy.text(f"SELECT cart_id FROM carts WHERE customer_id = '{temp_customer_id}'")).fetchone()
        temp_cart_id = result_temp_id.cart_id
        
    return {"cart_id": temp_cart_id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    color = "green" #if you dont tell me your getting green
    if item_sku == "RED_POTION":
        color = "red"
    elif item_sku == "GREEN_POTION":
        color = "green"
    elif item_sku == "BLUE_POTION":
        color = "blue"


    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE carts SET {color}_potion = {cart_item.quantity} WHERE cart_id = {cart_id}"))
        
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    print("--checkout--")
    """ """

    with db.engine.begin() as connection:
        result_red_potions_sold = connection.execute(sqlalchemy.text(f"SELECT red_potion from carts where cart_id = {cart_id}")).fetchone()
        red_potions_sold = result_red_potions_sold.red_potion
        result_green_potions_sold = connection.execute(sqlalchemy.text(f"SELECT green_potion from carts where cart_id = {cart_id}")).fetchone()
        green_potions_sold = result_green_potions_sold.green_potion
        result_blue_potions_sold = connection.execute(sqlalchemy.text(f"SELECT blue_potion from carts where cart_id = {cart_id}")).fetchone()
        blue_potions_sold = result_blue_potions_sold.blue_potion

        balance = (red_potions_sold * 50) + (green_potions_sold * 50) + (blue_potions_sold * 50)
        total_potions = red_potions_sold + green_potions_sold + blue_potions_sold
        print(f"checkout: balance = {balance}, payment = {cart_checkout.payment}")
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold + {balance}"))

        connection.execute(sqlalchemy.text(f"UPDATE potions SET amount = amount - {red_potions_sold} WHERE color = 'red'"))
        connection.execute(sqlalchemy.text(f"UPDATE potions SET amount = amount - {green_potions_sold} WHERE color = 'green'"))
        connection.execute(sqlalchemy.text(f"UPDATE potions SET amount = amount - {blue_potions_sold} WHERE color = 'blue'"))



    return {"total_potions_bought": total_potions, "total_gold_paid": balance}
