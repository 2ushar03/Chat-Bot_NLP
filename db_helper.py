import mysql.connector

cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="restaurant_data"
)


def get_next_orderid():
    cursor = cnx.cursor()

    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)
    res = cursor.fetchone()[0]
    cursor.close()

    if res is None:
        return 1
    else:
        return res+1


def get_total_order_price(order_id):
    cursor = cnx.cursor()
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)
    res = cursor.fetchone()[0]
    cursor.close()
    return res


def insert_order_item(food, qty, order_id):
    try:
        cursor = cnx.cursor()

        cursor.callproc("insert_order_item", (food, qty, order_id))

        cnx.commit()

        cursor.close()

        print("Order Inserted Successfully! ")
        return 1

    except mysql.connector.Error as err:
        print(f"Error in inserting item: {err}")
        cnx.rollback()
        return -1

    except Exception as e:
        print(f"An Error Occured: {e}")
        cnx.rollback()

        return -1


def get_order_status(order_id: int):
    cursor = cnx.cursor()

    query = "SELECT status FROM order_tracking WHERE order_id = %s"

    cursor.execute(query, (order_id,))

    result = cursor.fetchone()

    cursor.close()
    if result is not None:
        return result[0]
    else:
        return None


def insert_order_tracking(order_id, status):
    cursor = cnx.cursor()
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))
    cnx.cursor()
    cursor.close()
