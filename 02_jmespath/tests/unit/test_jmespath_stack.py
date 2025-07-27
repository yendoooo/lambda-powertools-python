import aws_cdk as core
import aws_cdk.assertions as assertions

from jmespath.jmespath_stack import JmespathStack

# example tests. To run these tests, uncomment this file along with the example
# resource in lambda_powertools_python/lambda_powertools_python_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = JmespathStack(app, "jmespath")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
