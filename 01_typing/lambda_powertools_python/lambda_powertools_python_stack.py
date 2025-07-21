from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class LambdaPowertoolsPythonStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda Layer: Powertools for AWS Lambda (Python)
        # Layer ARN: https://docs.powertools.aws.dev/lambda/python/latest/#lambda-layer
        layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "PowertoolsLayer",
            layer_version_arn=f"arn:aws:lambda:ap-northeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python311-x86_64:20"
        )

        # Lambda 関数: Typing 機能未使用版
        function_before =_lambda.Function(
            self,
            "FunctionBefore",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="function_before.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
        )

        # Lambda 関数: Typing 機能使用版
        function_after = _lambda.Function(
            self,
            "FunctionAfter",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="function_after.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[layer],
        )

        CfnOutput(
            self,
            "FunctionBeforeName",
            value=function_before.function_name,
            export_name="FunctionBeforeName",
        )

        CfnOutput(
            self,
            "FunctionAfterName",
            value=function_after.function_name,
            export_name="FunctionAfterName",
        )
