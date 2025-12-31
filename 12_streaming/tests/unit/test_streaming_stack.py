import aws_cdk as core
import aws_cdk.assertions as assertions

from streaming.streaming_stack import StreamingStack

# example tests. To run these tests, uncomment this file along with the example
# resource in streaming/streaming_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = StreamingStack(app, "streaming")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
