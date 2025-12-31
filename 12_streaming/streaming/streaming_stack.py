from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from constructs import Construct


class StreamingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 バケット: 注文データ保存用
        bucket = s3.Bucket(
            self,
            "OrderDataBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Lambda Layer: Powertools for AWS Lambda (Python)
        layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "PowertoolsLayer",
            layer_version_arn="arn:aws:lambda:ap-northeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python311-x86_64:20",
        )

        # Lambda 関数
        function = _lambda.Function(
            self,
            "Function",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[layer],
            timeout=Duration.minutes(5),
            memory_size=256,
            environment={
                "POWERTOOLS_SERVICE_NAME": "order-aggregator",
                "POWERTOOLS_LOG_LEVEL": "INFO",
            },
        )

        # S3 読み取り権限を付与
        bucket.grant_read(function)

        # 出力
        CfnOutput(
            self,
            "BucketName",
            value=bucket.bucket_name,
            export_name="OrderDataBucketName",
        )

        CfnOutput(
            self,
            "FunctionName",
            value=function.function_name,
            export_name="StreamingFunctionName",
        )