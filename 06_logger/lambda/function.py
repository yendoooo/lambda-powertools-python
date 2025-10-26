import json
from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

# Logger のインスタンス化 (サンプリング設定付き)
logger = Logger(
    service="payment",
    sampling_rate=0.1,  # 10% の確率で DEBUG レベルのログを出力
)


@logger.inject_lambda_context(
    log_event=True,  # イベントのロギングを有効化 (開発環境のみ推奨)
    clear_state=True,  # 各呼び出し後にカスタムキーをクリア
)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Logger 機能使用"""

    # ユーザー情報の取得
    user_id = event.get("body", {}).get("user_id")
    amount = event.get("body", {}).get("amount", 0)

    # 永続的なキーの追加 (このリクエスト中のすべてのログに含まれる)
    logger.append_keys(user_id=user_id)

    logger.info("Starting payment process")

    # DEBUG レベルのログ (サンプリングにより 10% の確率でのみ出力される)
    logger.debug(
        "Payment validation details",
        extra={
            "validation_rules": ["amount_positive", "user_exists"],
            "amount": amount,
        },
    )

    # 処理ステップごとのログ
    logger.info("Validating payment request")

    # メタデータ付きログ出力 (extra パラメータ)
    logger.info(
        "Payment details validated", extra={"amount": amount, "currency": "JPY"}
    )

    try:
        # 決済処理のシミュレーション
        if amount <= 0:
            logger.warning("Invalid payment amount", extra={"amount": amount})
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid amount"})}

        # 追加のコンテキスト情報をログに含める
        payment_id = f"PAY-{user_id}-{amount}"
        logger.append_keys(payment_id=payment_id)

        logger.info("Payment processed")
        logger.debug("Payment processing completed successfully")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Payment successful", "payment_id": payment_id}
            ),
        }

    except ValueError as e:
        # 特定の例外のハンドリング
        logger.exception("Validation error occurred")
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
    except Exception:
        # 予期しない例外
        logger.exception("Unexpected error during payment processing")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
