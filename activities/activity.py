import logging
from temporalio import activity
from helpers.db_logic import order_received, order_validated, payment_charged, order_shipped, package_prepared, carrier_dispatched
from models.model import Order, Payment, Event


@activity.defn
async def order_received_activity(order: Order) -> dict:
    logging.info(f"Received order {order}")
    return await order_received(order)

@activity.defn
async def order_validated_activity(order_id: str) -> bool:
    logging.info(f"Validating order {order_id}")
    return await order_validated(order_id)

@activity.defn
async def payment_charged_activity(order_id: str, payment: Payment) -> dict:
    logging.info(f"Charging payment {payment} for order {order_id}")
    return await payment_charged(order_id, payment)

@activity.defn
async def order_shipped_activity(order_id: str) -> str:
    logging.info(f"Shipping order {order_id}")
    return await order_shipped(order_id)

@activity.defn
async def package_prepared_activity(order_id: str) -> str:
    logging.info(f"Preparing package for order {order_id}")
    return await package_prepared(order_id)

@activity.defn
async def carrier_dispatched_activity(order_id: str) -> str:
    logging.info(f"Dispatching carrier for order {order_id}")
    return await carrier_dispatched(order_id)