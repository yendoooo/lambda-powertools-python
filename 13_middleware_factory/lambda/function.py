import json
from typing import Any

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from middlewares import add_security_headers, authorize_request, validate_order_request

logger = Logger(service="order-service")
tracer = Tracer(service="order-service")


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@add_security_headers
@authorize_request(allowed_roles=["admin", "operator"])
@validate_order_request
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """注文処理 Lambda ハンドラー"""
    body = event.get("body", {})

    order_id = body.get("order_id")
    customer_id = body.get("customer_id")
    items = body.get("items", [])

    logger.append_keys(order_id=order_id, customer_id=customer_id)

    # 注文処理のシミュレーション
    total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)

    logger.info("Order processed successfully", extra={"total_amount": total_amount})

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Order processed successfully",
            "order_id": order_id,
            "customer_id": customer_id,
            "total_amount": total_amount,
            "items_count": len(items),
        }),
    }