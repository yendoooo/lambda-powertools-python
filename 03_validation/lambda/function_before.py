import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Validation 機能未使用"""

    body: dict[str, Any] = json.loads(event["body"])

    try:
        # 手動でのバリデーション処理
        validation_errors = validate_user_data(body)

        if validation_errors:
            return {
                "statusCode": 400,
                "body": json.dumps({"errors": validation_errors}),
            }

        # ビジネスロジックの実行
        result = process_user_data(body)

        return {
            "statusCode": 200,
            "body": json.dumps(result),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


def validate_user_data(data: Dict[str, Any]) -> List[str]:
    """ユーザーデータの手動バリデーション"""
    errors = []

    # 必須フィールドの確認
    if "name" not in data:
        errors.append("Missing required field: name")
    elif not isinstance(data["name"], str) or len(data["name"].strip()) == 0:
        errors.append("Name must be a non-empty string")
    elif len(data["name"]) > 100:
        errors.append("Name must be less than 100 characters")

    if "email" not in data:
        errors.append("Missing required field: email")
    elif not isinstance(data["email"], str):
        errors.append("Email must be a string")
    elif "@" not in data["email"]:
        errors.append("Email format is invalid")

    # 年齢の検証 (任意フィールド)
    if "age" in data:
        age = data["age"]
        if not isinstance(age, int):
            errors.append("Age must be an integer")
        elif age < 0 or age > 150:
            errors.append("Age must be between 0 and 150")

    return errors


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
