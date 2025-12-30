import json
from datetime import datetime
from typing import Any
from uuid import uuid4

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    CORSConfig,
    Response,
    content_types,
)
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger(service="order-api")
tracer = Tracer(service="order-api")

# CORS 設定
cors_config = CORSConfig(
    allow_origin="https://example.com",
    allow_headers=["Content-Type", "Authorization"],
    max_age=300,
)

app = APIGatewayRestResolver(cors=cors_config)

# サンプルデータ (実際は DynamoDB などを使用)
orders_db: dict[str, dict[str, Any]] = {}


@app.get("/orders")
@tracer.capture_method
def get_orders():
    """全注文の取得"""
    status = app.current_event.get_query_string_value(name="status", default_value=None)
    limit = app.current_event.get_query_string_value(name="limit", default_value="10")

    orders = list(orders_db.values())

    if status:
        orders = [o for o in orders if o.get("status") == status]

    return {"orders": orders[: int(limit)], "count": len(orders)}


@app.get("/orders/<order_id>")
@tracer.capture_method
def get_order(order_id: str):
    """特定の注文を取得"""
    if order_id not in orders_db:
        raise NotFoundError(f"Order {order_id} not found")

    return {"order": orders_db[order_id]}


@app.post("/orders")
@tracer.capture_method
def create_order():
    """新規注文の作成"""
    body: dict[str, Any] = app.current_event.json_body

    required_fields = ["product_id", "quantity", "customer_id"]
    if not all(field in body for field in required_fields):
        raise BadRequestError("Missing required fields")

    order_id = str(uuid4())
    order = {
        "order_id": order_id,
        "product_id": body["product_id"],
        "quantity": body["quantity"],
        "customer_id": body["customer_id"],
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    orders_db[order_id] = order
    logger.info("Order created", extra={"order_id": order_id})

    return {"order": order}, 201


@app.put("/orders/<order_id>")
@tracer.capture_method
def update_order(order_id: str):
    """注文の更新"""
    if order_id not in orders_db:
        raise NotFoundError(f"Order {order_id} not found")

    body: dict[str, Any] = app.current_event.json_body

    for field in ["quantity", "status"]:
        if field in body:
            orders_db[order_id][field] = body[field]

    orders_db[order_id]["updated_at"] = datetime.now().isoformat()

    return {"order": orders_db[order_id]}


@app.delete("/orders/<order_id>")
@tracer.capture_method
def delete_order(order_id: str):
    """注文の削除"""
    if order_id not in orders_db:
        raise NotFoundError(f"Order {order_id} not found")

    del orders_db[order_id]

    return Response(
        status_code=204,
        content_type=content_types.APPLICATION_JSON,
        body="",
    )


@app.exception_handler(ValueError)
def handle_value_error(ex: ValueError):
    """ValueError のハンドリング"""
    logger.error(f"Validation error: {ex}")
    return Response(
        status_code=400,
        content_type=content_types.APPLICATION_JSON,
        body=json.dumps({"error": str(ex)}),
    )


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    return app.resolve(event, context)