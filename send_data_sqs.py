import argparse
from itertools import islice
import boto3
import json


def grouped(iterator, size):
    yield list(next(iterator) for _ in range(size))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Send messages to SQS queue")
    parser.add_argument("config", help="path to 'terraform output --json' config JSON")
    parser.add_argument("input_file", help="File with tasking, one per line")
    parser.add_argument(
        "--batch-size",
        "-b",
        dest="batch_size",
        default=10,
        type=int,
        help="Send data to a lambda in groups of this many",
    )
    args = parser.parse_args()

    # Parse config to extract queues
    with open(args.config, "r") as f:
        configs = json.load(f)["config"]["value"]

    queues = []
    for c in configs:
        sqs = boto3.resource("sqs", region_name=c["aws_region"])
        queues.append(sqs.Queue(c["queue_in_url"]))

    with open(args.input_file, "r") as f:
        # Read file in chunks
        i = 0
        while True:
            i += 1
            lines = list(islice(f, args.batch_size))
            if not lines:
                break
            queue = queues[i % len(queues)]
            messages = []
            for j in range(args.batch_size):
                messages.append(
                    {
                        # Messages have a per-batch ID
                        # As well as the message body
                        "Id": f"id-{j}",
                        "MessageBody": lines[j].strip(),
                    }
                )
            resp = queue.send_messages(Entries=messages)
            if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
                print("Error?")
            print(f"Sent {(i * args.batch_size)} messages to {queue.url}")
