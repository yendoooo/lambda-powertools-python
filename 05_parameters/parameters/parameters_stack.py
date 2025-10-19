import json

from aws_cdk import CfnOutput, Duration, SecretValue, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class ParametersStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda Layer: Powertools for AWS Lambda (Python)
        layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "PowertoolsLayer",
            layer_version_arn="arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python313-x86_64:23",
        )

        # SSM Parameter Store パラメータの作成
        api_endpoint_param = ssm.StringParameter(
            self,
            "ApiEndpoint",
            parameter_name="/myapp/api/endpoint",
            string_value="https://api.example.com/v1",
            description="API endpoint URL",
        )

        db_config_param = ssm.StringParameter(
            self,
            "DatabaseConfig",
            parameter_name="/myapp/database/config",
            string_value=json.dumps(
                {"host": "db.example.com", "port": 5432, "database": "myapp"}
            ),
            description="Database configuration (JSON)",
        )

        config_timeout = ssm.StringParameter(
            self,
            "ConfigTimeout",
            parameter_name="/myapp/config/timeout",
            string_value="30",
            description="Request timeout in seconds",
        )

        config_retry = ssm.StringParameter(
            self,
            "ConfigRetry",
            parameter_name="/myapp/config/retry",
            string_value="3",
            description="Number of retries",
        )

        config_log_level = ssm.StringParameter(
            self,
            "ConfigLogLevel",
            parameter_name="/myapp/config/log_level",
            string_value="INFO",
            description="Logging level",
        )

        feature_flags_param = ssm.StringParameter(
            self,
            "FeatureFlags",
            parameter_name="/myapp/feature/flags",
            string_value=json.dumps(
                {"new_feature_enabled": True, "beta_features": False}
            ),
            description="Feature flags configuration (JSON)",
        )

        # Secrets Manager シークレットの作成
        api_key_secret = secretsmanager.Secret(
            self,
            "ApiKeySecret",
            secret_name="/myapp/api/key",
            description="API Key for external service",
            secret_string_value=SecretValue.unsafe_plain_text("my-secret-key"),
        )

        # Lambda 関数
        function = _lambda.Function(
            self,
            "ParametersFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[layer],
            timeout=Duration.seconds(30),
            environment={
                "POWERTOOLS_SERVICE_NAME": "myapp",
                "POWERTOOLS_PARAMETERS_MAX_AGE": "300",  # デフォルトキャッシュ時間: 5分
            },
        )

        # IAM ポリシーの付与
        api_endpoint_param.grant_read(function)
        db_config_param.grant_read(function)
        feature_flags_param.grant_read(function)
        api_key_secret.grant_read(function)

        function.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=["ssm:GetParametersByPath"],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter/myapp/config"
                ],
            )
        )

        CfnOutput(
            self,
            "FunctionName",
            value=function.function_name,
            export_name="ParametersFunctionName",
        )
