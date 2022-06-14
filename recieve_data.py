from contextlib import ExitStack
import argparse
import json
import time
import boto3

def log(data, outf):
    print(data)
    if outf:
        outf.write(f"{data}\n")
        outf.flush()

def recieve_queues(args, queues, outf):
    for queue in queues:
        messages_to_delete = []
        messages = queue.receive_messages(
            MaxNumberOfMessages=args.batch_size, WaitTimeSeconds=1
        )
        for i, message in enumerate(messages):
            resp = json.loads(message.body)
            data = resp["data"]
            if args.unique_only:
                if data not in unique_data:
                    log(data, outf)
                    unique_data.append(data)
            else:
                log(data, outf)

            messages_to_delete.append(
                {"Id": f"id-{i}", "ReceiptHandle": message.receipt_handle}
            )

        # Remove messages from queue
        if len(messages_to_delete) > 0:
            queue.delete_messages(Entries=messages_to_delete)

        if len(messages) > 0 and args.unique_only:
            # Print 'summary' of messages
            print(f"[{len(messages):02}] .")
        time.sleep(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Recieve messages from SQS queues")
    parser.add_argument("config", help="path to 'terraform output --json' config JSON")
    parser.add_argument(
        "--unique-only",
        "-u",
        dest="unique_only",
        action="store_true",
        help="Only print unique responses",
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        dest="batch_size",
        default=10,
        type=int,
        help="Read data from SQS in batches of this",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Optional output file to stream to",
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
        with ExitStack():
            outf = open(args.output, "w", encoding="utf-8") if args.output else None
            while True:
                recieve_queues(args, queues, outf)
    except KeyboardInterrupt:
        pass
