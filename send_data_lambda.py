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
        config = json.load(f)

    func = "dothingi"
    clients = []
    for region in config["aws_region"]["value"]:
        clients.append(boto3.client("lambda", region_name=region))

    with open(args.input_file, "r") as f:
        # Read file in chunks
        i = 0
        while True:
            i += 1
            lines = list(islice(f, args.batch_size))
            if not lines:
                break
            client = clients[i % len(clients)]

            # Build JSON to match SQS Message format
            messages = []
            for j in range(args.batch_size):
                messages.append(
                    {
                        "messageId": lines[j].strip(),
                        "body": lines[j].strip(),
                    }
                )
            data = {"Records": messages}

            # Call lambda function
            resp = client.invoke(
                FunctionName=func,
                InvocationType="Event",
                Payload=json.dumps(data).encode(),
            )
            if resp["StatusCode"] < 200 or resp["StatusCode"] > 299:
                err = resp["Payload"].read().decode()
                print(f"Error invoking function: {err}")
                continue

            print(f"{(i * args.batch_size)} msg to {func} {client.meta.region_name}")
