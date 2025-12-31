from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_event_sources as event_sources
from aws_cdk import aws_logs as logs
from aws_cdk import aws_sqs as sqs
from constructs import Construct


class BatchProcessingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Dead Letter Queue
        dlq = sqs.Queue(
            self,
            "OrderDLQ",
            queue_name="order-dlq",
            retention_period=Duration.days(14),
        )

        # メインキュー
        queue = sqs.Queue(
            self,
            "OrderQueue",
            queue_name="order-queue",
            visibility_timeout=Duration.seconds(60),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=dlq,
            ),
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
            "Function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[layer],
            timeout=Duration.seconds(30),
            environment={
                "POWERTOOLS_SERVICE_NAME": "order-processor",
                "POWERTOOLS_LOG_LEVEL": "INFO",
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
            tracing=_lambda.Tracing.ACTIVE,
        )

        # SQS イベントソースマッピング (ReportBatchItemFailures 有効)
        function.add_event_source(
            event_sources.SqsEventSource(
                queue,
                batch_size=10,
                max_batching_window=Duration.seconds(5),
                report_batch_item_failures=True,  # 重要: 部分的な失敗レポートを有効化
            )
        )

        # 出力
        CfnOutput(self, "QueueUrl", value=queue.queue_url)
        CfnOutput(self, "DLQUrl", value=dlq.queue_url)
        CfnOutput(self, "FunctionName", value=function.function_name)