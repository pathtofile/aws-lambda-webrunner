# AWS Lambda Request Maker
Spreads out arbitrary web requests across multiple AWS Lambdas.

# Motivation
Plent of projects like this already exist, but I had a need to be able to easily 'spread out'
bulk web requests across multiple IPs, prefable also across multiple geographic reagions.

# Design
This project uses Terraform to setup multiple AWS Lambdas and [SQS Queues](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)
across one or more AWS regions. The lambdas are designed to attempt one or more HTTP requests, sending the response to an output SQS Queue.

The lambdas can be either tasked directly, or via an input SQS Queue (if provisioned). Data from the output SQS queue can then be retrieved and saved.

The [Send Data](./send_data.py) Python script is used to auto-generate URL requests to make. It takes in a template with the base URL details, and file containing a list of different requests to make (e.g. usernames to look up). It then sends the requests to the lambda in batches.

TODO: Add diagram


# Setup
## Deploy Terraform
Open the [main.tf terraform file](./main.tf). For each region to deploy lambdas to, copy both the `provider` and `module` blocks,
chaning the `region` variable. Also add the module to the `locals.modules` variable at the end. Optionally change the other variable values.

If `lambda_count` is more than 1, don't set `enable_input_queue`, otherwise this will drastically slow down the provisioning time.

Then Use terraform to createh environment:
```bash
terraform apply --auto-approve
```


## Create Input list of items to requests
Create an input file with a list of items to request, one per line.
E.g. If looking up a list of users, put one username per line.

If only requiring a counter (e.g. the items would just be the numbers 1-10 to represent page numbers), a file isn't required, and the range can be specified on the commandline.


## Create URL Config template
JSON Templates are used to automatically generate URL requests to send to the lambdas. Use the [GitHub Template](./url_config_github.jinja2) as an example. The only required field is `url`, `method` defaults to `GET` and everything defaults to empty. If response is expected to be JSON, set `json_response` to `true` to improve log output readability.

The template has two variables that will be auto-populated based on the input file:
 - `{{ line }}` - The line in the input textfile (e.g. the username)
 - `{{ line_num }}` - Either the line number, or ranger counter if no input file
 - `{{ counter }}` - Alias for `line_num`


## Install Python dependecies
Install the Python dependecies for the `send_data` and `get_data`
scripts:
```bash
python -m pip install -r requirements.txt
```

# Using
## Send data
Use the [send_data](./send_data.py) Script, passing in the outputted Terraform Config (to get the lambda and SQS URLs), the URL Template,
and any input file:
```bash
python send_data.py url_config_github.jinja2 --input-file users.txt
```

If using a range and not an input file, use `--range`:
```bash
# Set `line_num` as a counter from 0 to 10:
python send_data.py url_config_github.jinja2 --range 10

# Set `line_num` as a counter from 22 to 55 in batches of 5:
python send_data.py url_config_github.jinja2 --range 22-55 --batch-size 5

# For more options
python send_data.py --help
```

## Get data
You can either use the [get_data](./get_data.py) script, passing in the outputted Terraform config:
```bash
# Stream to stdout
python get_data.py

# Pretty-print
python get_data.py --pretty

# Also log to file
python get_data.py --output-file data.log

# Only get unique responses (filters out 404s, etc.)
python get_data.py --unique-only

# For more options
python get_data.py --help
```

Or you can get the results synchronously when sending the data:
```bash
# Stream to stdout
python send_data.py url_config_github.jinja2 --input-file users.txt --output

# Pretty-print
python send_data.py url_config_github.jinja2 --input-file users.txt --output-pretty

# Also log to file
python send_data.py url_config_github.jinja2 --input-file users.txt --output-file data.log
```

# Teardown
When finished use Terraform to destroy infra:
```bash
terraform destroy --auto-approve
```

# Links:
## Cost estimates:
https://aws.amazon.com/sqs/pricing/

## Misc
https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
https://docs.aws.amazon.com/lambda/latest/dg/with-sqs-example.html
https://www.youtube.com/watch?v=nhEFJgIhvuk
https://aws.amazon.com/blogs/compute/understanding-how-aws-lambda-scales-when-subscribed-to-amazon-sqs-queues/
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Queue.delete_messages
