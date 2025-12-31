import time
from typing import Any, Callable

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()


@lambda_handler_decorator(trace_execution=True)
def validate_order_request(
    handler: Callable[[dict, LambdaContext], dict],
    event: dict,
    context: LambdaContext,
) -> dict:
    """リクエスト検証ミドルウェア: 注文リクエストの必須フィールドを検証"""
    logger.info("Validating order request")

    body = event.get("body", {})
    required_fields = ["order_id", "customer_id", "items"]

    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        logger.warning("Missing required fields", extra={"missing_fields": missing_fields})
        return {
            "statusCode": 400,
            "body": {"error": f"Missing required fields: {missing_fields}"},
        }

    # 検証成功後、ハンドラーを実行
    return handler(event, context)


@lambda_handler_decorator(trace_execution=True)
def authorize_request(
    handler: Callable[[dict, LambdaContext], dict],
    event: dict,
    context: LambdaContext,
    allowed_roles: list[str] | None = None,
) -> dict:
    """認可ミドルウェア: ユーザーのロールに基づいてアクセスを制御"""
    logger.info("Authorizing request")

    headers = event.get("headers", {})
    user_role = headers.get("X-User-Role", "guest")

    tracer.put_annotation(key="UserRole", value=user_role)

    if allowed_roles and user_role not in allowed_roles:
        logger.warning("Unauthorized access attempt", extra={"user_role": user_role})
        return {
            "statusCode": 403,
            "body": {"error": "Access denied"},
        }

    # 認可成功後、ハンドラーを実行
    return handler(event, context)


@lambda_handler_decorator(trace_execution=True)
def add_security_headers(
    handler: Callable[[dict, LambdaContext], dict],
    event: dict,
    context: LambdaContext,
) -> dict:
    """セキュリティヘッダー付与ミドルウェア: レスポンスにセキュリティヘッダーを追加"""
    start_time = time.time()

    # ハンドラーを実行
    response = handler(event, context)

    execution_time = time.time() - start_time

    # セキュリティヘッダーを追加
    if "headers" not in response:
        response["headers"] = {}

    response["headers"].update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "X-Request-Id": context.aws_request_id,
        "X-Execution-Time": str(execution_time),
    })

    logger.info("Added security headers", extra={"execution_time": execution_time})

    return response