import argparse
import boto3

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Send messages to SQS queue")
    parser.add_argument("queue_url")
    args = parser.parse_args()

    sqs = boto3.client("sqs")
    queue = boto3.resource("sqs").Queue(args.queue_url)

    # Create list of messages
    messages = []
    for i in range(10):
        messages.append(
            {
                # Messages have a per-batch ID
                # As well as the message body
                "Id": f"id-{i}",
                "MessageBody": f"from_python_{i:02}",
            }
        )

    resp = queue.send_messages(Entries=messages)
    if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        print("Error?")
