from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
from datetime import datetime
from urllib.parse import urlencode


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

    with db.engine.begin() as connection:
        search = "SELECT customers.name AS name, potion_option_id, amount, price, sku, created_at FROM cart_log JOIN customers ON cart_log.customer_id = customers.customer_id JOIN cart_entry ON cart_entry.cart_id = cart_log.cart_id JOIN potion_option ON potion_option.id = cart_entry.potion_option_id"
        if customer_name or potion_sku:
            search += " WHERE "
        if customer_name:
            search += "customers.name = '"
            search += customer_name
            search += "'"
            if potion_sku:
                search += " and "
        if potion_sku:
            search += "sku = '"
            search += potion_sku
            search += "'"
        search += " ORDER BY created_at"

        result_orders = connection.execute(sqlalchemy.text(search)).fetchall()
    
    return_list = []
    line_id = 1 #+ ((int(search_page) - 1) * 5)
    while len(return_list) < 5 and line_id <= len(result_orders):
        time = datetime.fromisoformat(str(result_orders[line_id-1].created_at))
        return_list.append({
            "line_item_id": line_id,
            "item_sku": result_orders[line_id-1].sku,
            "customer_name": result_orders[line_id-1].name,
            "line_item_total": result_orders[line_id-1].amount * result_orders[line_id-1].price,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        line_id += 1

    previous = ""
    next = ""

    """if len(result_orders) > line_id:
        tags = {
        "customer_name": customer_name,
        "potion_sku": potion_sku,
        "search_page": str(int(search_page) - 1),
        "sort_col": sort_col,
        "sort_order": sort_order
        }
        #next = f"https://leaky-tap.onrender.com/carts/search/?{urlencode(tags)}"

    if int(search_page) > 1:
        tags = {
        "customer_name": customer_name,
        "potion_sku": potion_sku,
        "search_page": str(int(search_page) + 1),
        "sort_col": sort_col,
        "sort_order": sort_order
        }
        print("previous")"""

    
    for n in return_list:
        print(n)
        
    return {
        "previous": previous,
        "next": next,
        "results": return_list
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
        cart_entry = connection.execute(sqlalchemy.text("SELECT amount, potion_option_id from cart_entry WHERE cart_id = :temp_id"), {"temp_id": cart_id}).fetchall()
        customer_id = connection.execute(sqlalchemy.text("SELECT customer_id FROM cart_log WHERE cart_id = :temp_id"), {"temp_id": cart_id}).fetchone()[0]
        customer_name = connection.execute(sqlalchemy.text("SELECT name FROM customers WHERE customer_id = :temp_id"), {"temp_id": customer_id}).fetchone()[0]
        balance = 0
        total_potions = 0

        print(f"{customer_name}'s recipt:")
        for n in cart_entry:
            amount = n.amount
            potion_id = n.potion_option_id
            potion_info = connection.execute(sqlalchemy.text("SELECT price, name from potion_option WHERE id = :temp_id"), {"temp_id": potion_id}).fetchone()
            connection.execute(sqlalchemy.text("INSERT INTO potion_log (potion_id, amount) VALUES (:temp_potion_id, :temp_amount)"), {"temp_amount": -amount, "temp_potion_id": potion_id})

            price = potion_info.price
            potion_name = potion_info.name
            balance += (price * amount)
            total_potions += amount
            print(f"-{potion_name} x {amount}")
        

        connection.execute(sqlalchemy.text(f"UPDATE cart_log SET total_bought = {total_potions}, balance = {balance} WHERE cart_id = {cart_id}"))
        connection.execute(sqlalchemy.text("INSERT INTO gold (gold_diff) VALUES (:diff)"), {"diff": balance})

        print("price: ", balance)
        print("payment: ", cart_checkout.payment)
        return {"total_potions_bought": total_potions, "total_gold_paid": balance}
