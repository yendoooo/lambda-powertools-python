import aws_cdk as core
import aws_cdk.assertions as assertions

from idempotency.idempotency_stack import IdempotencyStack

# example tests. To run these tests, uncomment this file along with the example
# resource in idempotency/idempotency_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = IdempotencyStack(app, "idempotency")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
