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
    for n in customers:
        print(n)

    
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
    #print(f"making new cart for ", new_cart.customer_name)
    #version 1
    with db.engine.begin() as connection:
        customer_name = new_cart.customer_name
        result_customer = connection.execute(sqlalchemy.text(f"SELECT customer_id FROM customers WHERE name = '{customer_name}'")).fetchone()
        temp_customer_id = result_customer.customer_id

        print(f"creating cart for {customer_name}...")

        cart_id = connection.execute(sqlalchemy.text(f"INSERT INTO cart_log (customer_id) VALUES ({temp_customer_id}) RETURNING cart_id")).fetchone()[0]
        print(f"cart id: {cart_id}")
        
    return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):

    with db.engine.begin() as connection:
        with db.engine.begin() as connection:
           print("adding", cart_item.quantity, item_sku, "to cart", cart_id)
           potion_id = connection.execute(sqlalchemy.text(f"SELECT id FROM potion_option WHERE sku = '{item_sku}'")).fetchone()[0]
           connection.execute(sqlalchemy.text(f"INSERT INTO cart_entry (cart_id, potion_option_id, amount) VALUES ({cart_id}, {potion_id}, {cart_item.quantity})"))
        
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):

    with db.engine.begin() as connection:
        print("--checkout--")
        cart_entry = connection.execute(sqlalchemy.text(f"SELECT amount, potion_option_id from cart_entry WHERE cart_id = {cart_id}")).fetchall()
        customer_id = connection.execute(sqlalchemy.text(f"SELECT customer_id FROM cart_log WHERE cart_id = {cart_id}")).fetchone()[0]
        customer_name = connection.execute(sqlalchemy.text(f"SELECT name FROM customers WHERE customer_id = {customer_id}")).fetchone()[0]
        balance = 0
        total_potions = 0

        print(f"{customer_name}'s recipt:")
        for n in cart_entry:
            amount = n[0]
            potion_id = n[1]
            potion_info = connection.execute(sqlalchemy.text(f"SELECT price, name from potion_option WHERE id = {potion_id}")).fetchone()
            connection.execute(sqlalchemy.text(f"UPDATE potion_amount SET amount = (amount - {amount}) WHERE type_id = {potion_id}"))

            price = potion_info[0]
            potion_name = potion_info[1]
            balance += (price * amount)
            total_potions += amount
            print(f"-{potion_name} x {amount}")
        

        connection.execute(sqlalchemy.text(f"UPDATE cart_log SET total_bought = {total_potions}, balance = {balance} WHERE cart_id = {cart_id}"))
        return_gold = connection.execute(sqlalchemy.text("INSERT INTO gold_entry (gold_diff) VALUES (:diff) RETURNING entry_id"), {"diff": balance})
        connection.execute(sqlalchemy.text("UPDATE balance SET gold = gold + :gold_diff"), {"gold_diff": balance})

        print("price: ", balance)
        print("payment: ", cart_checkout.payment)
        return {"total_potions_bought": total_potions, "total_gold_paid": balance}
