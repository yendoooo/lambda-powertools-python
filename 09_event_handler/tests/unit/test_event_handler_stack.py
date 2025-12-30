import aws_cdk as core
import aws_cdk.assertions as assertions

from event_handler.event_handler_stack import EventHandlerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in event_handler/event_handler_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EventHandlerStack(app, "event-handler")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
