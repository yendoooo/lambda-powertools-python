from datetime import datetime, timezone
from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator
from schemas import USER_SCHEMA, RESPONSE_SCHEMA


@validator(inbound_schema=USER_SCHEMA, outbound_schema=RESPONSE_SCHEMA, envelope="powertools_json(body)")
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Validation 機能使用"""

    try:
        # バリデーション済みのデータを使用してビジネスロジックを実行
        result = process_user_data(event)

        return {
            "statusCode": 200,
            "body": result,
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
        }


def process_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """ユーザーデータの処理"""
    return {
        "message": "User data processed successfully",
        "user_id": "user_12345",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "processed_data": {
            "name": user_data["name"],
            "email": user_data["email"],
            "age": user_data.get("age"),
        }
    }
