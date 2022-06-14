import json
import os
import boto3
import urllib3


# # See this for details on how to use urllib3
# # https://urllib3.readthedocs.io/en/stable/user-guide.html
def do_request(task):
    method = task.get("method", "GET")
    headers = task.get("headers")
    params = task.get("params")
    url = task["url"]

    http = urllib3.PoolManager()
    resp = http.request(method, url, headers=headers, fields=params)
    output = {
        "lambda_name": os.environ["LambdaName"],
        "line": task["line"],
        "json_response": task["json_response"],
        "status": resp.status,
        "data": resp.data.decode().strip(),
    }

    return output


def lambda_handler(event, context):
    sqs = boto3.client("sqs")
    resp_queue = os.environ["ResponseQueueURL"]
    failures = []

    for record in event["Records"]:
        task = json.loads(record["body"])
        try:
            resp = do_request(task)
            sqs.send_message(
                QueueUrl=resp_queue,
                MessageBody=json.dumps(resp),
            )
        except:
            failures.append(record["messageId"])

    lambda_resp = {"batchItemFailures": failures}
    return {"statusCode": 200, "body": json.dumps(lambda_resp)}
