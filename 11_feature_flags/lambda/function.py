import json
from typing import Any

from aws_lambda_powertools.utilities.feature_flags import AppConfigStore, FeatureFlags
from aws_lambda_powertools.utilities.typing import LambdaContext

# AppConfigStore の初期化
app_config = AppConfigStore(
    environment="dev",
    application="ec-site",
    name="features",
    max_age=120,  # キャッシュ時間 (秒)
)

# FeatureFlags の初期化
feature_flags = FeatureFlags(store=app_config)


def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """EC サイトの機能制御を行う Lambda 関数

    以下のフィーチャーフラグを評価:
    - premium_features: tier が premium の場合に有効
    - winter_sale_campaign: 全顧客に対して有効/無効
    """
    # リクエストから顧客情報を取得
    customer_tier = event.get("tier", "standard")
    base_price = event.get("price", 1000)

    # コンテキストの作成 (ルール評価に使用)
    ctx = {"tier": customer_tier}

    # プレミアム機能の評価
    has_premium_features: bool = feature_flags.evaluate(
        name="premium_features",
        context=ctx,
        default=False,
    )

    # 冬季セールキャンペーンの評価 (静的フラグのためコンテキスト不要)
    apply_winter_sale: bool = feature_flags.evaluate(
        name="winter_sale_campaign",
        default=False,
    )

    # 割引の適用
    final_price = base_price
    discounts_applied = []

    if has_premium_features:
        # プレミアム会員は 20% 割引
        final_price *= 0.8
        discounts_applied.append("premium_discount_20%")

    if apply_winter_sale:
        # 冬季セールは追加 10% 割引
        final_price *= 0.9
        discounts_applied.append("winter_sale_10%")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "customer_tier": customer_tier,
            "original_price": base_price,
            "final_price": int(final_price),
            "discounts_applied": discounts_applied,
            "premium_features_enabled": has_premium_features,
            "winter_sale_enabled": apply_winter_sale,
        }),
    }