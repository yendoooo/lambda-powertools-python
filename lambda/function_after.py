import json
from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Typing 機能使用"""
    # context オブジェクトのプロパティにアクセス
    # IDE で自動補完とメソッドドキュメントが利用可能
    function_name = context.function_name
    request_id = context.aws_request_id
    memory_limit = context.memory_limit_in_mb
    remaining_time = context.get_remaining_time_in_millis()

    # event の処理
    user_id = event.get("user_id")
    message = event.get("message", "Hello World")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message,
            "user_id": user_id,
            "lambda_info": {
                "function_name": function_name,
                "request_id": request_id,
                "memory_limit": memory_limit,
                "remaining_time_ms": remaining_time
            }
        })
    }
