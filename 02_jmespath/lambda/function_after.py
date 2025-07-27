import json
from datetime import datetime, timezone
from typing import Any

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.jmespath_utils import query


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """JMESPath Functions 機能使用"""

    try:
        # リクエストボディの取得・デコード
        body_query: str = """
        isBase64Encoded && powertools_json(powertools_base64(body)) || powertools_json(body)
        """
        request_data = query(data=event, envelope=body_query)

        # 条件に基づくフィルタリング
        active_users_query: str = """
        data.users[?status == 'active' && age >= `18`].{
            id: id,
            name: profile.name,
            email: contact.email,
            department: work.department
        }
        """
        active_users = query(data=request_data, envelope=active_users_query)

        # レスポンスの構築
        response_data: dict = {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "total_users": query(data=request_data, envelope="length(data.users)"),
            "active_users_count": len(active_users) if active_users else 0,
            "active_users": active_users or [],
            "source_ip": query(data=event, envelope="requestContext.identity.sourceIp")
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