from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class MiddlewareFactoryStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda Layer: Powertools for AWS Lambda (Python)
        layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "PowertoolsLayer",
            layer_version_arn="arn:aws:lambda:ap-northeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python311-x86_64:20"
        )

        # Lambda 関数
        function = _lambda.Function(
            self,
            "OrderFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[layer],
            timeout=Duration.seconds(30),
            tracing=_lambda.Tracing.ACTIVE,  # X-Ray トレーシングを有効化
            environment={
                "POWERTOOLS_SERVICE_NAME": "order-service",
                "POWERTOOLS_LOG_LEVEL": "INFO",
                "POWERTOOLS_TRACE_MIDDLEWARES": "true",  # ミドルウェアのトレースを有効化
            }
        )

        # 出力
        CfnOutput(
            self,
            "FunctionName",
            value=function.function_name,
            export_name="OrderFunctionName",
        )