import json

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_appconfig as appconfig
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class FeatureFlagsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # フィーチャーフラグの設定
        features_config = {
            "premium_features": {
                "default": False,
                "rules": {
                    "customer tier equals premium": {
                        "when_match": True,
                        "conditions": [
                            {
                                "action": "EQUALS",
                                "key": "tier",
                                "value": "premium",
                            }
                        ],
                    }
                },
            },
            "winter_sale_campaign": {
                "default": True,
            },
        }

        # AWS AppConfig Application
        config_app = appconfig.CfnApplication(
            self,
            "FeatureStoreApp",
            name="ec-site",
            description="EC サイト用 AppConfig Application",
        )

        # AWS AppConfig Environment
        config_env = appconfig.CfnEnvironment(
            self,
            "FeatureStoreDevEnv",
            application_id=config_app.ref,
            name="dev",
            description="開発環境",
        )

        # AWS AppConfig Configuration Profile (Freeform)
        config_profile = appconfig.CfnConfigurationProfile(
            self,
            "FeatureStoreConfigProfile",
            application_id=config_app.ref,
            name="features",
            location_uri="hosted",
        )

        # AWS AppConfig Hosted Configuration Version
        hosted_config_version = appconfig.CfnHostedConfigurationVersion(
            self,
            "HostedConfigVersion",
            application_id=config_app.ref,
            configuration_profile_id=config_profile.ref,
            content=json.dumps(features_config),
            content_type="application/json",
        )

        # AWS AppConfig Deployment (即時デプロイ)
        appconfig.CfnDeployment(
            self,
            "ConfigDeployment",
            application_id=config_app.ref,
            configuration_profile_id=config_profile.ref,
            configuration_version=hosted_config_version.ref,
            deployment_strategy_id="AppConfig.AllAtOnce",
            environment_id=config_env.ref,
        )

        # Lambda Layer: Powertools for AWS Lambda (Python)
        layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "PowertoolsLayer",
            layer_version_arn="arn:aws:lambda:ap-northeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:23",
        )

        # Lambda 関数
        function = _lambda.Function(
            self,
            "FeatureFlagsFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[layer],
        )

        # AppConfig 読み取り権限の付与
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "appconfig:GetLatestConfiguration",
                    "appconfig:StartConfigurationSession",
                ],
                resources=["*"],
            )
        )

        CfnOutput(
            self,
            "FunctionName",
            value=function.function_name,
            export_name="FeatureFlagsFunctionName",
        )