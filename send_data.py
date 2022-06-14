import argparse
from itertools import islice
import boto3
import json
import random
from jinja2 import Template


def gen_body(uconfig_txt, line, line_num):
    txt = Template(uconfig_txt).render(line=line, line_num=line_num)

    uconfig = json.loads(txt)
    task = {
        "url": uconfig["url"],
        "line": line,
        "json_response": uconfig.get("json_response", True),
    }
    for c in ["method", "headers", "params"]:
        if c in uconfig:
            task[c] = uconfig[c]
    return json.dumps(task)


def send_lamda(i, lines, funcs, batch_size):
    func = funcs[i % len(funcs)]
    func_name = func["func_name"]
    client = func["client"]

    # Build JSON to match SQS Message format
    messages = []
    for j, line in enumerate(lines):
        line_num = (i * batch_size) + j
        body = gen_body(uconfig_txt, line.strip(), line_num)
        messages.append({"messageId": f"id-{j}", "body": body})
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
        return

    print(f"Sent {len(lines)} messages to {func_name} {client.meta.region_name}")


def send_sqs(i, lines, queues, batch_size):
    queue = queues[i % len(queues)]
    messages = []
    for j, line in enumerate(lines):
        line_num = (i * batch_size) + j
        body = gen_body(uconfig_txt, line.strip(), line_num)
        messages.append(
            {
                # Messages have a per-batch ID
                # As well as the message body
                "Id": f"id-{j}",
                "MessageBody": body,
            }
        )
    resp = queue.send_messages(Entries=messages)
    if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        print("Error?")
    print(f"Sent {len(lines)} messages to {queue.url}")


def parse_file(args, queues, funcs):
    with open(args.input, "r") as f:
        # Read file in chunks
        i = 0
        while True:
            lines = list(islice(f, args.batch_size))
            if not lines:
                break
            if args.use_sqs:
                send_sqs(i, lines, queues, args.batch_size)
            else:
                send_lamda(i, lines, funcs, args.batch_size)
            i += 1


def parse_range(args, queues, funcs):
    final = int(args.input)
    i = 0
    while True:
        start = i * args.batch_size
        stop = min(final, start + args.batch_size)
        lines = [str(i) for i in range(start, stop)]
        if args.use_sqs:
            send_sqs(i, lines, queues, args.batch_size)
        else:
            send_lamda(i, lines, funcs, args.batch_size)
        if stop >= final:
            break
        i += 1
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Send messages to SQS queue")
    parser.add_argument(
        "tf_config", help="path to 'terraform output --json' config JSON"
    )
    parser.add_argument(
        "url_config", help="path to URL config JSON detailing ULS, headers, etc"
    )
    parser.add_argument(
        "--use-sqs",
        "-s",
        action="store_true",
        dest="use_sqs",
        help="Use input SQS queue",
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        dest="batch_size",
        default=10,
        type=int,
        help="Send data to a lambda in groups of this many",
    )
    parser.add_argument(
        "--input",
        "-i",
        help="either a file with tasking, one per line, or a number or requests to make",
    )
    parser.add_argument(
        "--input-type",
        "-it",
        dest="input_type",
        default="file",
        choices=["file", "range"],
        help="input is either a file with tasking, one per line, or a number or requests to make",
    )
    args = parser.parse_args()

    # Parse config to extract queues
    with open(args.tf_config, "r") as f:
        configs = json.load(f)["config"]["value"]

    with open(args.url_config, "r") as f:
        uconfig_txt = f.read()

    # 'flatten' list of region and func to make it easier
    # to spread the load out
    funcs = []
    queues = []
    for config in configs:
        for func in config["lambda_funcs"]:
            funcs.append(
                {
                    "client": boto3.client("lambda", region_name=config["aws_region"]),
                    "func_name": func,
                }
            )
        if args.use_sqs:
            sqs = boto3.resource("sqs", region_name=config["aws_region"])
            queues.append(sqs.Queue(config["queue_in_url"]))
    random.shuffle(funcs)

    if args.input_type == "file":
        parse_file(args, queues, funcs)
    else:
        parse_range(args, queues, funcs)
