import json
import logging
from datetime import datetime, timezone

from aws_lambda_powertools.utilities.typing import LambdaContext

logger = logging.getLogger(__name__)


def lambda_handler(event: dict[str, any], context: LambdaContext) -> dict[str, any]:
    """Parser 機能未使用"""
    
    try:
        # イベントボディの解析
        body = json.loads(event.get("body", "{}"))
        
        # 手動でのデータ検証
        validation_errors = validate_order_data(body)
        if validation_errors:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Validation failed",
                    "details": validation_errors
                })
            }
        
        # ビジネスロジックの実行
        result = process_order(body)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
        
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON format"})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e!s}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }


def validate_order_data(data: dict[str, any]) -> list[str]:
    """手動でのデータ検証"""
    errors = []
    
    # 注文IDの検証
    if "order_id" not in data:
        errors.append("order_id is required")
    elif not isinstance(data["order_id"], str) or not data["order_id"].strip():
        errors.append("order_id must be a non-empty string")
    
    # 顧客情報の検証
    if "customer" not in data:
        errors.append("customer information is required")
    else:
        customer = data["customer"]
        if not isinstance(customer, dict):
            errors.append("customer must be an object")
        else:
            if "customer_id" not in customer:
                errors.append("customer.customer_id is required")
            if "name" not in customer:
                errors.append("customer.name is required")
            if "email" not in customer:
                errors.append("customer.email is required")
            elif "@" not in customer["email"]:
                errors.append("customer.email format is invalid")
    
    # 商品リストの検証
    if "items" not in data:
        errors.append("items are required")
    else:
        items = data["items"]
        if not isinstance(items, list) or len(items) == 0:
            errors.append("items must be a non-empty array")
        else:
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"items[{i}] must be an object")
                    continue
                
                if "product_id" not in item:
                    errors.append(f"items[{i}].product_id is required")
                if "product_name" not in item:
                    errors.append(f"items[{i}].product_name is required")
                if "quantity" not in item:
                    errors.append(f"items[{i}].quantity is required")
                elif not isinstance(item["quantity"], int) or item["quantity"] <= 0:
                    errors.append(f"items[{i}].quantity must be a positive integer")
                if "unit_price" not in item:
                    errors.append(f"items[{i}].unit_price is required")
                elif not isinstance(item["unit_price"], (int, float)) or item["unit_price"] <= 0:
                    errors.append(f"items[{i}].unit_price must be a positive number")
    
    return errors


def process_order(order_data: dict[str, any]) -> dict[str, any]:
    """注文処理"""
    
    # 合計金額の計算
    total_amount = sum(
        item["quantity"] * item["unit_price"] 
        for item in order_data.get("items", [])
    )
    
    return {
        "message": "Order processed successfully",
        "order_id": order_data["order_id"],
        "customer_id": order_data["customer"]["customer_id"],
        "total_amount": total_amount,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "status": "confirmed"
    }