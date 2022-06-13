import argparse
import json
import time
import boto3

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Recieve messages from SQS queues")
    parser.add_argument("config", help="path to 'terraform output --json' config JSON")
    parser.add_argument(
        "--print", "-p", action="store_true", help="Print each message response"
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        dest="batch_size",
        default=10,
        type=int,
        help="Read data from SQS in batches of this",
    )
    args = parser.parse_args()

    # Parse config to extract queues
    with open(args.config, "r") as f:
        configs = json.load(f)["config"]["value"]

    queues = []
    for c in configs:
        sqs = boto3.resource("sqs", region_name=c["aws_region"])
        queues.append(sqs.Queue(c["queue_out_url"]))

    unique_data = []
    try:
        while True:
            for queue in queues:
                messages_to_delete = []
                messages = queue.receive_messages(
                    MaxNumberOfMessages=args.batch_size, WaitTimeSeconds=1
                )
                for i, message in enumerate(messages):
                    resp = json.loads(message.body)
                    data = resp["data"]
                    if args.print:
                        print(data)
                    else:
                        if data not in unique_data:
                            unique_data.append(data)
                            print(f"[*] {len(unique_data)} | {data}")
                    messages_to_delete.append(
                        {"Id": f"id-{i}", "ReceiptHandle": message.receipt_handle}
                    )

                # Remove messages from queue
                if len(messages_to_delete) > 0:
                    queue.delete_messages(Entries=messages_to_delete)

                if len(messages) > 0 and not args.print:
                    print(f"[{len(messages):02}] .")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    if not args.print:
        print("------------------")
        print(f"Unique IPs: {len(unique_data)}")
        print("\n".join(unique_data))
