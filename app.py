#!/usr/bin/env python3
import aws_cdk as cdk

from powertools.powertools_stack import PowertoolsStack


app = cdk.App()

stack: PowertoolsStack = PowertoolsStack(app, 'Stack')
cdk.RemovalPolicies.of(stack).destroy()

app.synth()
