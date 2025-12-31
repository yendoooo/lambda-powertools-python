import json
import os
from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_masking import DataMasking
from aws_lambda_powertools.utilities.data_masking.provider.kms.aws_encryption_sdk import (
    AWSEncryptionSDKProvider,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

# KMS キー ARN の取得
KMS_KEY_ARN = os.getenv("KMS_KEY_ARN", "")

# Logger のインスタンス化
logger = Logger(service="order-processing")

# 暗号化プロバイダーのインスタンス化
encryption_provider = AWSEncryptionSDKProvider(keys=[KMS_KEY_ARN])

# Data Masking のインスタンス化
data_masker = DataMasking(provider=encryption_provider)


@logger.inject_lambda_context
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """注文処理 Lambda 関数"""

    order = event.get("order", {})
    operation = event.get("operation", "erase")

    logger.info("Processing order", extra={"operation": operation})

    if operation == "erase":
        # 機密情報の消去 (ログ出力用)
        masked_order = erase_sensitive_data(order)
        logger.info("Order processed (masked for logging)", extra={"order": masked_order})
        return {"statusCode": 200, "body": json.dumps(masked_order)}

    elif operation == "encrypt":
        # 機密情報の暗号化 (データベース保存用)
        encrypted_order = encrypt_sensitive_data(order)
        logger.info("Order encrypted for storage")
        return {"statusCode": 200, "body": json.dumps(encrypted_order)}

    elif operation == "decrypt":
        # 暗号化データの復号化
        decrypted_order = decrypt_sensitive_data(order)
        logger.info("Order decrypted")
        return {"statusCode": 200, "body": json.dumps(decrypted_order)}

    return {"statusCode": 400, "body": json.dumps({"error": "Invalid operation"})}


def erase_sensitive_data(order: dict[str, Any]) -> dict[str, Any]:
    """機密データを不可逆的に消去"""

    # 消去対象フィールドの指定
    fields_to_erase = [
        "customer.email",
        "customer.phone",
        "payment.card_number",
        "payment.cvv",
        "shipping.address.street",
    ]

    # データの消去
    return data_masker.erase(order, fields=fields_to_erase)


def erase_with_custom_mask(order: dict[str, Any]) -> dict[str, Any]:
    """カスタムマスクを使用した消去"""

    # フィールドごとに異なるマスキングルールを適用
    masking_rules = {
        "customer.email": {
            "regex_pattern": r"(.)(.*)(@.*)",
            "mask_format": r"\1****\3",
        },
        "payment.card_number": {"dynamic_mask": True},
        "payment.cvv": {"custom_mask": "XXX"},
    }

    return data_masker.erase(order, masking_rules=masking_rules)


def encrypt_sensitive_data(order: dict[str, Any]) -> str:
    """機密データの暗号化"""

    # 暗号化コンテキストを指定して暗号化
    return data_masker.encrypt(
        order,
        data_classification="confidential",
        data_type="order-data",
    )


def decrypt_sensitive_data(encrypted_data: str) -> dict[str, Any]:
    """暗号化データの復号化"""

    # 暗号化時と同じコンテキストを指定して復号化
    return data_masker.decrypt(
        encrypted_data,
        data_classification="confidential",
        data_type="order-data",
    )