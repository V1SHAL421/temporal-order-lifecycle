from typing import Dict, Any
from .timeout_simulation_helper import flaky_call
from ..models.model import Order, Payment, Event
import sqlite3
from uuid import uuid4
import time
import json
import logging

async def order_received(order: Order) -> Dict[str, Any]:
    """
    Insert received order into table in database

    Args:
    - order (Order): Order data from received order

    Returns:
    - order_data (dict): Updated order data with timestamps, ID and state

    Raises:
    - Exception: Error occurred
    """
    try:
        await flaky_call()
        
        order_id = str(uuid4())
        logging.info(f"Processing order received for order_id: {order_id}")
        created_at = str(time.time())
        updated_at = created_at
        order_data = order.model_dump()
        order_data["id"] = order_id
        order_data["state"] = "received"
        order_data["created_at"] = created_at
        order_data["updated_at"] = updated_at

        con = sqlite3.connect("./data/order_lifecycle.db")
        cur = con.cursor()

        cur.execute("""
            INSERT INTO orders (id, state, address_json, items_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            order_data['id'],
            order_data['state'], 
            order_data['address_json'],
            order_data['items_json'],
            order_data['created_at'],
            order_data['updated_at']
        ))
        
        # Insert event
        cur.execute("""
            INSERT INTO events (id, order_id, type, payload_json, ts)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid4()),
            order_id,
            "order_received",
            json.dumps(order_data),
            created_at
        ))
        
        con.commit()
        con.close()
        return order_data
    except Exception as e:
        logging.error(f"Error processing order received: {e}")
        raise e

async def order_validated(order_id: str) -> bool:
    """
    Validate order by checking if all items have a valid SKU and quantity.

    Args:
    - order_id (str): Order ID to validate

    Returns:
    - Boolean (bool): Order is validated or not
    """
    try:
        await flaky_call()
        logging.info(f"Validating order: {order_id}")
        
        con = sqlite3.connect("./data/order_lifecycle.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cur.fetchone()

        if not row:
            raise ValueError("Order not found")
        
        items_json_string = row[3]
        items = json.loads(items_json_string)
        if not items:
            con.close()
            return False
        
        for item in items:
            if not item.get("sku") or item.get("qty", 0) <= 0:
                con.close()
                return False
        
        # Update state to validated
        timestamp = str(time.time())
        cur.execute("UPDATE orders SET state = ?, updated_at = ? WHERE id = ?", 
                    ("validated", timestamp, order_id))
        
        # Insert event
        cur.execute("""
            INSERT INTO events (id, order_id, type, payload_json, ts)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid4()),
            order_id,
            "order_validated",
            json.dumps({"validated": True}),
            timestamp
        ))
        
        con.commit()
        con.close()
        return True
    except Exception as e:
        logging.error(f"Error validating order: {e}")
        raise e

async def payment_charged(order_id: str, payment: Payment) -> Dict[str, Any]:
    """
    Charge payment for order.

    Args:
    - order_id (str): Order ID to charge payment for
    - payment (Payment): Payment data

    Returns:
    - payment_data (dict): Updated payment data with IDs, timestamps and status change

    Raises:
    - Exception: Error occurred
    """
    await flaky_call()
    logging.info(f"Charging payment for order: {order_id}")
    
    try:
        con = sqlite3.connect("./data/order_lifecycle.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cur.fetchone()

        if not row:
            raise ValueError("Order not found")
        items_json_string = row[3]
        items = json.loads(items_json_string)
        amount = sum(i.get("qty", 1) for i in items)
        if not amount:
            raise ValueError("No items found")
        payment_id = str(uuid4())
        # Assuming each item costs $1
        total_payment = amount * 100
        payment_data = payment.model_dump()
        payment_data["payment_id"] = payment_id
        payment_data["order_id"] = order_id
        payment_data["status"] = "charged"
        payment_data["amount"] = total_payment
        payment_data["created_at"] = str(time.time())
        payment_data["updated_at"] = payment_data["created_at"]

        con = sqlite3.connect("./data/order_lifecycle.db")
        cur = con.cursor()
        cur.execute("""
            INSERT INTO payments (payment_id, order_id, status, amount, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payment_data['payment_id'],
            payment_data['order_id'],
            payment_data['status'],
            payment_data['amount'],
            payment_data['created_at'],
            payment_data['updated_at']
        ))
        
        # Insert event
        cur.execute("""
            INSERT INTO events (id, order_id, type, payload_json, ts)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid4()),
            order_id,
            "payment_charged",
            json.dumps(payment_data),
            payment_data['created_at']
        ))
        
        con.commit()
        con.close()
        return payment_data
    except Exception as e:
        logging.error(f"Error processing payment: {e}")
        raise e

async def order_shipped(order_id: str) -> str:
    """
    Update order status to shipped in database.

    Args:
    - order_id (str): Order ID to mark as shipped

    Returns:
    - str: Confirmation message

    Raises:
    - Exception: Error occurred
    """
    try:
        await flaky_call()
        logging.info(f"Shipping order: {order_id}")
        
        con = sqlite3.connect("./data/order_lifecycle.db")
        cur = con.cursor()
        timestamp = str(time.time())
        cur.execute("UPDATE orders SET state = ?, updated_at = ? WHERE id = ?", 
                    ("shipped", timestamp, order_id))
        
        # Insert event
        cur.execute("""
            INSERT INTO events (id, order_id, type, payload_json, ts)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid4()),
            order_id,
            "order_shipped",
            json.dumps({"status": "shipped"}),
            timestamp
        ))
        
        con.commit()
        con.close()
        return "Shipped"
    except Exception as e:
        logging.error(f"Error shipping order: {e}")
        raise e

async def package_prepared(order_id: str) -> str:
    """
    Update order status to package prepared in database.

    Args:
    - order_id (str): Order ID to mark as package prepared

    Returns:
    - str: Confirmation message

    Raises:
    - Exception: Error occurred
    """
    try:
        await flaky_call()
        logging.info(f"Preparing package for order: {order_id}")
        
        con = sqlite3.connect("./data/order_lifecycle.db")
        cur = con.cursor()
        timestamp = str(time.time())
        cur.execute("UPDATE orders SET state = ?, updated_at = ? WHERE id = ?", 
                    ("package_prepared", timestamp, order_id))
        
        # Insert event
        cur.execute("""
            INSERT INTO events (id, order_id, type, payload_json, ts)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid4()),
            order_id,
            "package_prepared",
            json.dumps({"status": "package_prepared"}),
            timestamp
        ))
        
        con.commit()
        con.close()
        return "Package ready"
    except Exception as e:
        logging.error(f"Error preparing package: {e}")
        raise e

async def carrier_dispatched(order_id: str) -> str:
    """
    Update order status to dispatched in database.

    Args:
    - order_id (str): Order ID to mark as dispatched

    Returns:
    - str: Confirmation message

    Raises:
    - Exception: Error occurred
    """
    try:
        await flaky_call()
        logging.info(f"Dispatching carrier for order: {order_id}")
        
        con = sqlite3.connect("./data/order_lifecycle.db")
        cur = con.cursor()
        timestamp = str(time.time())
        cur.execute("UPDATE orders SET state = ?, updated_at = ? WHERE id = ?", 
                    ("dispatched", timestamp, order_id))
        
        # Insert event
        cur.execute("""
            INSERT INTO events (id, order_id, type, payload_json, ts)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(uuid4()),
            order_id,
            "carrier_dispatched",
            json.dumps({"status": "dispatched"}),
            timestamp
        ))
        
        con.commit()
        con.close()
        return "Dispatched"
    except Exception as e:
        logging.error(f"Error dispatching carrier: {e}")
        raise e
