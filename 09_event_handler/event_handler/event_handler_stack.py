from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from constructs import Construct


class EventHandlerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda Layer: Powertools for AWS Lambda (Python)
        layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "PowertoolsLayer",
            layer_version_arn="arn:aws:lambda:ap-northeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python311-x86_64:23",
        )

        # Lambda 関数
        function = _lambda.Function(
            self,
            "Function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[layer],
            timeout=Duration.seconds(30),
            environment={
                "POWERTOOLS_SERVICE_NAME": "order-api",
                "POWERTOOLS_LOG_LEVEL": "INFO",
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
            tracing=_lambda.Tracing.ACTIVE,
        )

        # API Gateway REST API
        api = apigw.RestApi(
            self,
            "OrderApi",
            rest_api_name="Order API",
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                tracing_enabled=True,
            ),
        )

        # Lambda 統合
        integration = apigw.LambdaIntegration(function)

        # /orders リソース
        orders = api.root.add_resource("orders")
        orders.add_method("GET", integration)
        orders.add_method("POST", integration)

        # /orders/{order_id} リソース
        order = orders.add_resource("{order_id}")
        order.add_method("GET", integration)
        order.add_method("PUT", integration)
        order.add_method("DELETE", integration)

        # 出力
        CfnOutput(self, "ApiEndpoint", value=api.url)
        CfnOutput(self, "FunctionName", value=function.function_name)