import aws_cdk as core
import aws_cdk.assertions as assertions

from middleware_factory.middleware_factory_stack import MiddlewareFactoryStack

# example tests. To run these tests, uncomment this file along with the example
# resource in middleware_factory/middleware_factory_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MiddlewareFactoryStack(app, "middleware-factory")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
