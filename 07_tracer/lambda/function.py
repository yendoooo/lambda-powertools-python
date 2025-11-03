import json
import os
from decimal import Decimal
from typing import Any

import boto3
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

# Tracer のインスタンス化
tracer = Tracer(service="payment-service")

# DynamoDB クライアントの初期化
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME", "")
table = dynamodb.Table(table_name)


@tracer.capture_method
def get_user_info(user_id: str) -> dict[str, Any]:
    """ユーザー情報の取得（DynamoDB から）"""
    # アノテーションの追加（検索可能）
    tracer.put_annotation(key="UserId", value=user_id)

    response = table.get_item(Key={"user_id": user_id})
    user_info = response.get("Item", {})

    # メタデータの追加（検索不可、詳細情報用）
    tracer.put_metadata(key="user_info", value=user_info)

    return user_info


@tracer.capture_method
def validate_payment(amount: Decimal, user_tier: str) -> bool:
    """決済金額の検証"""
    # ビジネスロジックに関連するアノテーションを追加
    tracer.put_annotation(key="UserTier", value=user_tier)
    tracer.put_annotation(key="Amount", value=str(amount))

    # ユーザーの階層に応じた上限チェック
    limits = {
        "basic": Decimal("10000"),
        "premium": Decimal("100000"),
        "enterprise": Decimal("1000000"),
    }

    limit = limits.get(user_tier, Decimal("10000"))
    is_valid = amount <= limit

    tracer.put_metadata(
        key="validation_result",
        value={
            "limit": str(limit),
            "amount": str(amount),
            "is_valid": is_valid,
        },
    )

    return is_valid


@tracer.capture_method
def process_payment(payment_id: str, amount: Decimal) -> dict[str, Any]:
    """決済処理の実行"""
    tracer.put_annotation(key="PaymentId", value=payment_id)

    # 決済処理のシミュレーション
    result = {
        "payment_id": payment_id,
        "status": "completed",
        "amount": str(amount),
    }

    tracer.put_metadata(key="payment_result", value=result)

    return result


@tracer.capture_lambda_handler
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Lambda ハンドラー"""
    try:
        # イベントからパラメータを取得
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id")
        amount = Decimal(str(body.get("amount", 0)))

        if not user_id or amount <= 0:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid request parameters"}),
            }

        # ユーザー情報の取得
        user_info = get_user_info(user_id)
        if not user_info:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User not found"}),
            }

        # 決済金額の検証
        user_tier = user_info.get("tier", "basic")
        if not validate_payment(amount, user_tier):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Payment amount exceeds limit"}),
            }

        # 決済処理の実行
        payment_id = f"PAY-{user_id}-{context.aws_request_id[:8]}"
        result = process_payment(payment_id, amount)

        return {
            "statusCode": 200,
            "body": json.dumps(result),
        }

    except ValueError:
        # 特定の例外のハンドリング
        tracer.put_annotation(key="ErrorType", value="ValueError")
        raise

    except Exception:
        # 予期しない例外
        tracer.put_annotation(key="ErrorType", value="UnexpectedError")
        raise
