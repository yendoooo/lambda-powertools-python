import json
from datetime import datetime, timezone

from aws_lambda_powertools.utilities.parser import ValidationError, event_parser, envelopes
from aws_lambda_powertools.utilities.typing import LambdaContext

from schemas import Order


@event_parser(model=Order, envelope=envelopes.ApiGatewayEnvelope)
def lambda_handler(event: Order, context: LambdaContext) -> dict[str, any]:
    """Parser 機能使用"""
    
    try:
        # 自動的に解析・検証されたデータを使用
        result = process_order(event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }


def process_order(order: Order) -> dict[str, any]:
    """注文処理"""
    
    # Pydantic モデルのメソッドを直接使用
    total_amount = order.calculate_total()
    
    # 型安全なアクセス
    return {
        "message": "Order processed successfully",
        "order_id": order.order_id,
        "customer_id": order.customer.customer_id,
        "customer_name": order.customer.name,
        "items_count": len(order.items),
        "total_amount": total_amount,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "status": order.status.value
    }