import json
import base64
from datetime import datetime, timezone
from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """JMESPath Functions 機能未使用"""

    try:
        # リクエストボディの取得・デコード
        body: str = event.get("body", "{}")
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode('utf-8')

        request_data = json.loads(body)

        # ユーザー情報の抽出
        users: list = request_data.get("data", {}).get("users", [])

        # 条件に基づくフィルタリング
        active_users: list = []
        for user in users:
            if user.get("status") == "active" and user.get("age", 0) >= 18:
                active_users.append({
                    "id": user.get("id"),
                    "name": user.get("profile", {}).get("name"),
                    "email": user.get("contact", {}).get("email"),
                    "department": user.get("work", {}).get("department")
                })

        # レスポンスの構築
        response_data: dict = {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "total_users": len(users),
            "active_users_count": len(active_users),
            "active_users": active_users,
            "source_ip": event.get("requestContext", {}).get("identity", {}).get("sourceIp")
        }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response_data)
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }