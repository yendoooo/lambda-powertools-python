import json
from decimal import Decimal
from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.streaming import S3Object
from aws_lambda_powertools.utilities.streaming.transformations import (
    CsvTransform,
    GzipTransform,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger(service="order-aggregator")


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """
    gzip 圧縮された CSV ファイルをストリーミング処理し、
    注文データを集計する Lambda 関数

    期待する CSV フォーマット:
    order_id,customer_id,product_name,quantity,unit_price,order_date
    """
    bucket = event["bucket"]
    key = event["key"]

    logger.info("Starting order data aggregation", extra={"bucket": bucket, "key": key})

    # S3Object を使用してストリーミング処理
    # is_gzip=True, is_csv=True を指定することで、
    # gzip 解凍と CSV パースを自動的に適用
    s3_object = S3Object(bucket=bucket, key=key, is_gzip=True, is_csv=True)

    # 集計用の変数
    total_orders = 0
    total_revenue = Decimal("0")
    products: dict[str, dict[str, Any]] = {}
    customers: set[str] = set()

    # ストリーミングで 1 行ずつ処理
    # メモリに全データを読み込まずに処理できる
    for row in s3_object:
        total_orders += 1

        # 売上計算
        quantity = int(row["quantity"])
        unit_price = Decimal(row["unit_price"])
        revenue = quantity * unit_price
        total_revenue += revenue

        # 商品別集計
        product_name = row["product_name"]
        if product_name not in products:
            products[product_name] = {"quantity": 0, "revenue": Decimal("0")}
        products[product_name]["quantity"] += quantity
        products[product_name]["revenue"] += revenue

        # ユニーク顧客数
        customers.add(row["customer_id"])

        # 進捗ログ (1000 件ごと)
        if total_orders % 1000 == 0:
            logger.debug(f"Processed {total_orders} orders")

    # 商品別売上をソート (売上順)
    top_products = sorted(
        [
            {"name": name, "quantity": data["quantity"], "revenue": float(data["revenue"])}
            for name, data in products.items()
        ],
        key=lambda x: x["revenue"],
        reverse=True,
    )[:10]

    result = {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "unique_customers": len(customers),
        "unique_products": len(products),
        "top_products": top_products,
    }

    logger.info("Order aggregation completed", extra=result)

    return {
        "statusCode": 200,
        "body": json.dumps(result, ensure_ascii=False),
    }