# AWS Lambda Request Maker
Spreads out arbitrary web requests across multiple AWS Lambdas.

# Motivation
Plent of projects like this already exist, but I had a need to be able to easily 'spread out'
bulk web requests across multiple IPs, prefable also across multiple geographic reagions.

# Design
This project uses Terraform to setup multiple AWS Lambdas and [SQS Queues](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)
across one or more AWS regions. You manually send a number of requests to the lambdas to run, which will then 













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

```bash
python -c "print('\n'.join(['x'+str(i) for i in range(1000)]))" > input.txt
```

## Costs:
https://aws.amazon.com/sqs/pricing/

# Links
https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
https://docs.aws.amazon.com/lambda/latest/dg/with-sqs-example.html
https://www.youtube.com/watch?v=nhEFJgIhvuk
https://aws.amazon.com/blogs/compute/understanding-how-aws-lambda-scales-when-subscribed-to-amazon-sqs-queues/
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Queue.delete_messages


https://us-west-1.console.aws.amazon.com/lambda/home?region=us-west-1#/functions/dothingi?tab=code
https://us-west-1.console.aws.amazon.com/cloudwatch/home?region=us-west-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fdothingi
https://us-west-1.console.aws.amazon.com/sqs/v2/home?region=us-west-1#/queues
https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/roles


# Alternative:
Call function directly with batches of 10 messages:
    https://stackoverflow.com/questions/39456309/using-boto-to-invoke-lambda-functions-how-do-i-do-so-asynchronously
TODO: Test if this results in more IP Addressses?

python .\send_data.py .\tf_config.json .\url_config_ip.json.jinja2 --input 3 --input-type range -b 10
python .\recieve_data.py .\tf_config.json -o output.json
