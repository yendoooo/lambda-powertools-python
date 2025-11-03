from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class TracerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table
        table = dynamodb.Table(
            self,
            "Table",
            partition_key=dynamodb.Attribute(
                name="user_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Lambda Layer
        layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "Layer",
            layer_version_arn="arn:aws:lambda:ap-northeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python311-x86_64:23",
        )

        # Lambda Function
        function = _lambda.Function(
            self,
            "Function",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[layer],
            timeout=Duration.seconds(10),
            tracing=_lambda.Tracing.ACTIVE,  # X-Ray トレーシングを有効化
            environment={
                "TABLE_NAME": table.table_name,
                "POWERTOOLS_SERVICE_NAME": "payment-service",
                "POWERTOOLS_TRACER_CAPTURE_RESPONSE": "true",  # レスポンスキャプチャ
                "POWERTOOLS_TRACER_CAPTURE_ERROR": "true",  # 例外キャプチャ
            },
        )

        # DynamoDB テーブルへの読み取り権限を付与
        table.grant_read_data(function)

        # Outputs
        CfnOutput(
            self,
            "FunctionName",
            value=function.function_name,
            export_name="FunctionName",
        )

        CfnOutput(
            self,
            "TableName",
            value=table.table_name,
            export_name="TableName",
        )
