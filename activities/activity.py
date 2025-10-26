import asyncio
import logging
from temporalio import activity
from helpers.db_logic import order_received, order_validatd, payment_charged, order_shipped, package_prepared, carrier_dispatched



@activity.defn
async def order_received_activity(order_id: str) -> dict:
    logging.info(f"Received order {order_id}")
    return await order_received(order_id)

@activity.defn
async def order_validated_activity(order: dict) -> bool:
    logging.info(f"Validating order {order}")
    return await order_validatd(order)

@activity.defn
async def payment_charged_activity(order: dict, payment: dict) -> dict:
    logging.info(f"Charging payment {payment} for order {order}")
    return await payment_charged(order, payment)

@activity.defn
async def order_shipped_activity(order: dict) -> str:
    logging.info(f"Shipping order {order}")
    return await order_shipped(order)

@activity.defn
async def package_prepared_activity(order: dict) -> str:
    logging.info(f"Preparing package for order {order}")
    return await package_prepared(order)

@activity.defn
async def carrier_dispatched_activity(order: dict) -> str:
    logging.info(f"Dispatching carrier for order {order}")
    return await carrier_dispatched(order)