import json
import os
from decimal import Decimal
from typing import Any

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricResolution, MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

# 環境変数から取得
STAGE = os.getenv("STAGE", "dev")

# Metrics のインスタンス化
metrics = Metrics(service="ecommerce-api")

# デフォルトディメンションの設定
metrics.set_default_dimensions(environment=STAGE)


def validate_order(order_data: dict[str, Any]) -> bool:
    """注文データのバリデーション"""
    required_fields = ["order_id", "product_id", "quantity", "price"]

    # バリデーションの成功/失敗をメトリクスとして記録
    if not all(field in order_data for field in required_fields):
        metrics.add_metric(
            name="OrderValidationFailure", unit=MetricUnit.Count, value=1
        )
        return False

    if order_data["quantity"] <= 0 or order_data["price"] <= 0:
        metrics.add_metric(
            name="OrderValidationFailure", unit=MetricUnit.Count, value=1
        )
        return False

    # バリデーション成功
    metrics.add_metric(name="OrderValidationSuccess", unit=MetricUnit.Count, value=1)
    return True


def calculate_total_amount(price: Decimal, quantity: int) -> Decimal:
    """合計金額の計算"""
    total = price * quantity

    # 高解像度メトリクスで注文金額を記録 (1秒の粒度)
    metrics.add_metric(
        name="OrderAmount",
        unit=MetricUnit.None_,
        value=float(total),
        resolution=MetricResolution.High,
    )

    return total


def process_order(order_data: dict[str, Any]) -> dict[str, Any]:
    """注文処理"""
    order_id = order_data["order_id"]
    product_id = order_data["product_id"]
    quantity = order_data["quantity"]
    price = Decimal(str(order_data["price"]))

    # ディメンションを追加して特定の商品の注文数を追跡
    metrics.add_dimension(name="product_id", value=product_id)

    # 商品ごとの注文数をメトリクスとして記録
    metrics.add_metric(name="OrdersPerProduct", unit=MetricUnit.Count, value=1)

    # 合計金額の計算
    total_amount = calculate_total_amount(price, quantity)

    # メタデータとして高カーディナリティデータを追加
    # (メトリクスの可視化では利用できないが、ログでの検索に有用)
    metrics.add_metadata(
        key="order_details",
        value={
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "total_amount": str(total_amount),
        },
    )

    # 処理成功メトリクス
    metrics.add_metric(name="OrderProcessed", unit=MetricUnit.Count, value=1)

    return {
        "order_id": order_id,
        "status": "processed",
        "total_amount": str(total_amount),
    }


@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """
    E コマース注文処理の Lambda ハンドラー

    Metrics の log_metrics デコレーターにより:
    - すべてのメトリクスが関数終了時に自動的にフラッシュされる
    - メトリクスのバリデーションが実行される
    - capture_cold_start_metric=True によりコールドスタートメトリクスが別途記録される
    """
    try:
        # イベントから注文データを取得
        order_data = event.get("order", {})

        # バリデーション
        if not validate_order(order_data):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid order data"}),
            }

        # 注文処理
        result = process_order(order_data)

        # API レスポンスの成功メトリクス
        metrics.add_metric(name="APISuccess", unit=MetricUnit.Count, value=1)

        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception:
        # エラーメトリクス
        metrics.add_metric(name="APIError", unit=MetricUnit.Count, value=1)

        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
