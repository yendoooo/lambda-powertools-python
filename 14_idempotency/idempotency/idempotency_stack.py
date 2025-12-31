from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class IdempotencyStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB テーブル: Idempotency 状態管理用
        idempotency_table = dynamodb.Table(
            self,
            "IdempotencyTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="expiration",  # TTL 属性
            point_in_time_recovery=True,
        )

        # Lambda Layer: Powertools for AWS Lambda (Python)
        layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "PowertoolsLayer",
            layer_version_arn="arn:aws:lambda:ap-northeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:7",
        )

        # Lambda 関数
        function = _lambda.Function(
            self,
            "PaymentFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[layer],
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "IDEMPOTENCY_TABLE": idempotency_table.table_name,
                "POWERTOOLS_SERVICE_NAME": "payment",
                "POWERTOOLS_LOG_LEVEL": "INFO",
            },
        )

        # Lambda 関数に DynamoDB テーブルへのアクセス権限を付与
        idempotency_table.grant(
            function,
            "dynamodb:GetItem",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
        )

        # 出力
        CfnOutput(
            self,
            "FunctionName",
            value=function.function_name,
            export_name="PaymentFunctionName",
        )

        CfnOutput(
            self,
            "IdempotencyTableName",
            value=idempotency_table.table_name,
            export_name="IdempotencyTableName",
        )