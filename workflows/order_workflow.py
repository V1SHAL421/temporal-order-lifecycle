from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
from ..activities.activity import order_received_activity, order_validated_activity
from ..models.model import Order

@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order: Order) -> dict:
        workflow.logger.info(f"Received order {order}")

        result = await workflow.execute_activity(
            order_received_activity,
            order,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=10),
                backoff_coefficient=2
            )
        )

        workflow.logger.info(f"Order received: {result}")
        
        # Validate the order
        order_id = result["id"]
        is_valid = await workflow.execute_activity(
            order_validated_activity,
            order_id,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=10),
                backoff_coefficient=2
            )
        )

        if not is_valid:
            workflow.logger.error(f"Order validation failed: {order_id}")
            raise ValueError(f"Order validation failed: {order_id}")
        
        workflow.logger.info(f"Order validation result: {is_valid}")
        return result