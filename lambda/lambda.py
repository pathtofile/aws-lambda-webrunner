import json
import os
import boto3


def lambda_handler(event, context):
    sqs = boto3.client("sqs")
    queue_url = os.environ["ResponseQueueURL"]
    failures = []

    for record in event["Records"]:
        data = record["body"]
        print(f"ResponseQueueURL: {queue_url}")
        print(f"Data: {data}")

        # if failure_thing:
        #     failures.append(record["messageId"])

        response_data = f"Returining message {data}"
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=response_data,
        )

    lambda_resp = {"batchItemFailures": failures}
    return {"statusCode": 200, "body": json.dumps(lambda_resp)}
