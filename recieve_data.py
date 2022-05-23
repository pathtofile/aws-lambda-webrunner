import argparse
import time
import boto3

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Send messages to SQS queue")
    parser.add_argument("queue_url")
    args = parser.parse_args()

    sqs = boto3.client("sqs")
    queue = boto3.resource("sqs").Queue(args.queue_url)

    while True:
        messages_to_delete = []
        for i, message in enumerate(queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=1)):
            print(f"[*] {message.body}")
            messages_to_delete.append(
                {
                    "Id": f"id-{i}",
                    "ReceiptHandle": message.receipt_handle
                }
            )

        # Remove messages from queue
        if len(messages_to_delete) > 0:
            queue.delete_messages(Entries=messages_to_delete)
        print(".")
        time.sleep(1)
