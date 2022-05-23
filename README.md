# Bulk thing do-er thing using AWS

Testing using AWS SQS (Simple Queue Service) and Lambda to run lots of concurent *things*
that once, and store results.


# Design
## Creation
Host machine creates queues and lamda function, and links them together.

## SQS Queue #1
Mass-push tasking onto queue, one "target" (IP to scan, API call to make, etc.) per message.

# Lambda
Messages are sent in bulk (batch of 10?) to a lamda to do something with it.
Lambda takes messages one at a time, does a thing, and pushes responsed onto queue #2

## SQS Queue #2
Host Machines polls Queue #1 till it is empty (or a problem?), then pulls results from Queue #2
to get results.


# Links
https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
https://docs.aws.amazon.com/lambda/latest/dg/with-sqs-example.html
https://www.youtube.com/watch?v=nhEFJgIhvuk
https://aws.amazon.com/blogs/compute/understanding-how-aws-lambda-scales-when-subscribed-to-amazon-sqs-queues/
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function

