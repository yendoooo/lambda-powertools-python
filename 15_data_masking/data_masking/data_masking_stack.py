from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class DataMaskingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # KMS キーの作成
        encryption_key = kms.Key(
            self,
            "DataMaskingKey",
            description="KMS key for Data Masking encryption/decryption",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
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
            timeout=Duration.seconds(30),
            memory_size=1024,  # 暗号化処理は CPU 集約型のため 1024MB 以上を推奨
            environment={
                "POWERTOOLS_SERVICE_NAME": "order-processing",
                "POWERTOOLS_LOG_LEVEL": "INFO",
                "KMS_KEY_ARN": encryption_key.key_arn,
            },
        )

        # KMS キーへのアクセス許可
        encryption_key.grant(
            function,
            "kms:Decrypt",
            "kms:GenerateDataKey",
        )

        # 出力
        CfnOutput(
            self,
            "FunctionName",
            value=function.function_name,
            export_name="DataMaskingFunctionName",
        )

        CfnOutput(
            self,
            "KmsKeyArn",
            value=encryption_key.key_arn,
            export_name="DataMaskingKmsKeyArn",
        )