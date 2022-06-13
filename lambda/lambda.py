import json
import os
import boto3
import urllib3


# # See this for details on how to use urllib3
# # https://urllib3.readthedocs.io/en/stable/user-guide.html
def do_request(method, url, headers, params):
    http = urllib3.PoolManager()
    resp = http.request(method, url, headers=headers, fields=params)
    output = {
        "name": os.environ["LambdaName"],
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
        url = task["url"]
        method = task["method"] if "method" in task else "GET"
        headers = task["headers"] if "headers" in task else None
        params = task["params"] if "params" in task else None

        data = None
        try:
            resp = do_request(method, url, headers, params)
            sqs.send_message(
                QueueUrl=resp_queue,
                MessageBody=json.dumps(resp),
            )
        except:
            pass
        if data is None:
            failures.append(record["messageId"])

    lambda_resp = {"batchItemFailures": failures}
    return {"statusCode": 200, "body": json.dumps(lambda_resp)}
