from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_help

app = FastAPI()

processing_orders = {}


@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = generic_help.extract_sessionId(output_contexts[0]['name'])

    intent_handler = {
        "order.add - context: ongoing-order": added_order,
        "order.complete -context:ongoing-order": complete_order,
        "track.order -context:ongoing - tracking": track_order,
        'order.remove -context:ongoing-order': remove_from_order,
        'new.order': new_order,
    }

    return intent_handler[intent](parameters, session_id)


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in processing_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble in finding your Order. Kindly place a New Order"
        })
    cur_order = processing_orders[session_id]
    food_items = parameters["food-item"]

    removed_items = []
    no_such_items = []

    for i in food_items:
        if i not in cur_order:
            no_such_items.append(i)
        else:
            removed_items.append(i)
            del cur_order[i]
    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your Order!'

    if len(no_such_items) > 0:
        fulfillment_text = f'Your current Order not contains {",".join(no_such_items)}'

    if len(cur_order.keys()) == 0:
        fulfillment_text = "Cart is Empty!"

    else:
        ordered_elt = generic_help.get_str_from_dict(cur_order)
        fulfillment_text = f"Updated Cart {ordered_elt}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def complete_order(parameters: dict, session_id: str):
    if session_id not in processing_orders:
        fulfillment_text = "I'm having a trouble looking for your Order. Kindly place it again."
    else:
        order = processing_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillment_text = "Sorry, Unable to place the order. Kindly place it again after some time."

        else:
            # order_tot = db_helper.get_total_order_price(order_id)
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. Order Placed. "\
             f"Here is your Order Id #{order_id}." \
             f"Your Total Amount is {order_total}." \
             f"You can pay it Cash on Delivery"

        del processing_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def save_to_db(order: dict):
    next_orderid = db_helper.get_next_orderid()
    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(
            food_item,
            quantity,
            next_orderid
        )

        if rcode == -1:
            return -1

    db_helper.insert_order_tracking(next_orderid, "In progress")

    return next_orderid


def added_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]
    if len(food_items) != len(quantities):
        fulfillment_text = "Didn't get that. Please specify quantity and food item"
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in processing_orders:
            curr_items = processing_orders[session_id]
            curr_items.update(new_food_dict)
            processing_orders[session_id] = curr_items
        else:
            processing_orders[session_id] = new_food_dict

        order_str = generic_help.get_str_from_dict(processing_orders[session_id])
        fulfillment_text = f"Current order you have: {order_str}. Anything else?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict, session_id: str):
    order_id = parameters.get("number")
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order id {order_id} is {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def new_order(parameters: dict, session_id: str):
    if session_id in processing_orders:
        del processing_orders[session_id]
        return JSONResponse(content={
            "fulfillmentText": "Your cart has been cleared. You can start a new order now."
        })
    else:
        return JSONResponse(content={})

