import argparse
from itertools import islice
import boto3
import json
import random

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

    # 'flatten' list of region and func to make it easier
    # to spread the load out

    funcs = []
    for config in configs:
        for func in config["lambda_funcs"]:
            funcs.append({
                "client": boto3.client("lambda", region_name=config["aws_region"]),
                "func_name": func
            })
    random.shuffle(funcs)

    with open(args.input_file, "r") as f:
        # Read file in chunks
        i = 0
        while True:
            i += 1
            lines = list(islice(f, args.batch_size))
            if not lines:
                break
            func = funcs[i % len(funcs)]
            func_name = func["func_name"]
            client = func["client"]

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
                FunctionName=func_name,
                InvocationType="Event",
                Payload=json.dumps(data).encode(),
            )
            if resp["StatusCode"] < 200 or resp["StatusCode"] > 299:
                err = resp["Payload"].read().decode()
                print(f"Error invoking function: {err}")
                continue

            print(f"{(i * args.batch_size)} msg to {func_name} {client.meta.region_name}")
