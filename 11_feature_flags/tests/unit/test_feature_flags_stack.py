import aws_cdk as core
import aws_cdk.assertions as assertions

from feature_flags.feature_flags_stack import FeatureFlagsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in feature_flags/feature_flags_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FeatureFlagsStack(app, "feature-flags")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
