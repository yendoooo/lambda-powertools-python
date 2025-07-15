from aws_cdk import Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from constructs import Construct


class PowertoolsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        _lambda.Function(
            self,
            "Function",
            code=_lambda.Code.from_asset_image(
                directory='.',
                file='src/Dockerfile',
            ),
            handler=_lambda.Handler.FROM_IMAGE,
            runtime=_lambda.Runtime.FROM_IMAGE,
            log_retention=logs.RetentionDays.ONE_DAY,
        )
