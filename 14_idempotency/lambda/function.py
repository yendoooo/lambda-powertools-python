import json
import os
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.idempotency import (
    DynamoDBPersistenceLayer,
    IdempotencyConfig,
    idempotent_function,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

# Logger のインスタンス化
logger = Logger(service="payment")

# DynamoDB 永続化レイヤーの設定
table = os.getenv("IDEMPOTENCY_TABLE", "")
persistence_layer = DynamoDBPersistenceLayer(table_name=table)

# Idempotency 設定
# user_id と product_id の組み合わせを冪等キーとして使用
# amount フィールドでペイロード改ざんを検知
config = IdempotencyConfig(
    event_key_jmespath='["user_id", "product_id"]',
    payload_validation_jmespath="amount",
    expires_after_seconds=3600,  # 1 時間後に期限切れ
    use_local_cache=True,  # インメモリキャッシュを有効化
)


@dataclass
class Payment:
    """決済情報を表すデータクラス"""

    user_id: str
    product_id: str
    amount: int
    payment_id: str = field(default_factory=lambda: f"PAY-{uuid4()}")


class PaymentError(Exception):
    """決済処理エラー"""

    pass


@idempotent_function(
    data_keyword_argument="payment_data",
    config=config,
    persistence_store=persistence_layer,
)
def process_payment(payment_data: dict[str, Any]) -> Payment:
    """
    決済処理を行う関数（冪等性を保証）

    同じ user_id と product_id の組み合わせで呼び出された場合、
    以前の成功結果を返す
    """
    logger.info("Creating payment", extra={"payment_data": payment_data})

    # バリデーション
    if payment_data.get("amount", 0) <= 0:
        raise PaymentError("Invalid amount: must be positive")

    return Payment(
        user_id=payment_data["user_id"],
        product_id=payment_data["product_id"],
        amount=payment_data["amount"],
    )


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """決済処理を行う Lambda ハンドラー"""
    try:
        # Lambda タイムアウト対策のため、コンテキストを登録
        config.register_lambda_context(context)

        # リクエストボディのパース
        body = event.get("body", "{}")
        if isinstance(body, str):
            payment_data = json.loads(body)
        else:
            payment_data = body

        logger.info(
            "Processing payment request",
            extra={
                "user_id": payment_data.get("user_id"),
                "product_id": payment_data.get("product_id"),
            },
        )

        # 決済処理の実行（キーワード引数で呼び出す必要あり）
        payment = process_payment(payment_data=payment_data)

        logger.info(
            "Payment processed successfully",
            extra={"payment_id": payment.payment_id},
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Payment processed successfully",
                    "payment_id": payment.payment_id,
                    "user_id": payment.user_id,
                    "product_id": payment.product_id,
                    "amount": payment.amount,
                }
            ),
        }

    except PaymentError as e:
        logger.warning("Payment validation failed", extra={"error": str(e)})
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)}),
        }
    except Exception as e:
        logger.exception("Unexpected error during payment processing")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }