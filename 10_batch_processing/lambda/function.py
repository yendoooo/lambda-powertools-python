import json
from typing import Any

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    process_partial_response,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger(service="order-processor")
tracer = Tracer(service="order-processor")

processor = BatchProcessor(event_type=EventType.SQS)


@tracer.capture_method
def record_handler(record: SQSRecord):
    """各レコードを処理するハンドラー"""
    payload: dict[str, Any] = record.json_body

    logger.info("Processing order", extra={"order": payload})

    # 注文データのバリデーション
    if "order_id" not in payload:
        raise ValueError("Missing order_id")

    order_id = payload["order_id"]
    product_id = payload.get("product_id")
    quantity = payload.get("quantity", 0)

    # ビジネスロジック (実際は DB 保存など)
    if quantity <= 0:
        raise ValueError(f"Invalid quantity for order {order_id}")

    logger.info(
        "Order processed successfully",
        extra={
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
        },
    )

    return {"order_id": order_id, "status": "processed"}


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict[str, Any], context: LambdaContext):
    return process_partial_response(
        event=event,
        record_handler=record_handler,
        processor=processor,
        context=context,
    )