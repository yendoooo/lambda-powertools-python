import json
from typing import Any

from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.parameters.ssm import get_parameters_by_name
from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """Parameters 機能を使用した実装"""

    try:
        # === 基本的な使い方 ===

        # SSM Parameter Store から設定値を取得（自動キャッシュ）
        api_endpoint = parameters.get_parameter("/myapp/api/endpoint")

        # JSON 形式のパラメータを自動的にパース
        db_config = parameters.get_parameter("/myapp/database/config", transform="json")

        # Secrets Manager から機密情報を取得（自動キャッシュ）
        api_key = parameters.get_secret("/myapp/api/key")

        # 暗号化されたパラメータを自動復号化
        # NOTE: CDK で Secure String 型の parameter を定義できないため今回は省略
        # encrypted_value = parameters.get_parameter(
        #     "/myapp/encrypted/value", decrypt=True
        # )

        # === 応用: 複数パラメータの一括取得 ===

        # パス配下の全パラメータを一括取得
        all_configs = parameters.get_parameters(
            "/myapp/config",
            max_age=300,  # 5分間キャッシュ
        )

        # 特定の名前のパラメータを個別設定で取得
        specific_params = get_parameters_by_name(
            parameters={
                "/myapp/database/config": {
                    "transform": "json",
                    "max_age": 600,  # 10分間キャッシュ
                },
                "/myapp/feature/flags": {
                    "transform": "json",
                    "max_age": 0,  # キャッシュなし
                },
            },
            raise_on_error=False,  # 例外をスローするかどうか
        )

        # ビジネスロジックの実行
        result = process_request(
            api_endpoint=api_endpoint,
            db_config=db_config,
            api_key=api_key,
            all_configs=all_configs,
            specific_params=specific_params,
        )

        return {"statusCode": 200, "body": json.dumps(result, default=str)}

    except parameters.exceptions.GetParameterError as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def process_request(
    api_endpoint: str,
    db_config: dict,
    api_key: str,
    all_configs: dict,
    specific_params: dict,
) -> dict[str, Any]:
    """ビジネスロジック処理"""
    return {
        "message": "Request processed successfully",
        "endpoint": api_endpoint,
        "db_host": db_config.get("host"),
        "has_api_key": bool(api_key),
        "config_count": len(all_configs),
        "specific_params_count": len(specific_params),
    }
