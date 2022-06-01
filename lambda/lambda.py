import json
import os
import boto3
import urllib3


# See this for details on how to use urllib3
# https://urllib3.readthedocs.io/en/stable/user-guide.html
def do_stuff(input):
    http = urllib3.PoolManager()
    resp = http.request("GET", "https://ipv4.icanhazip.com")
    name = os.environ["LambdaName"]
    if resp.status == 200:
        ip_addr = resp.data.decode().strip()
        output = f"{name} | IP: {ip_addr}"
    else:
        output = f"{name} | Error: {resp.data}"

    print(f"[*] Message: {name} | {input} | {output}")
    return output


def lambda_handler(event, context):
    sqs = boto3.client("sqs")
    queue_url = os.environ["ResponseQueueURL"]
    failures = []

    for record in event["Records"]:
        input = record["body"]

        data = do_stuff(input)
        if data is None:
            failures.append(record["messageId"])

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=data,
        )

    lambda_resp = {"batchItemFailures": failures}
    return {"statusCode": 200, "body": json.dumps(lambda_resp)}
