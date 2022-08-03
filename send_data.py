import argparse
from itertools import islice
from types import SimpleNamespace
import boto3
import json
import random
import subprocess
from jinja2 import Template
from get_data import get_data

def gen_body(uconfig_txt, line, line_num):
    txt = Template(uconfig_txt).render(line=line, line_num=line_num, counter=line_num)

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
        return 0

    print(f"Sent {len(lines)} messages to {func_name} {client.meta.region_name}")
    return len(lines)


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
    return len(lines)


def parse_file(args, queues, funcs):
    total_lines = 0
    with open(args.input, "r") as f:
        # Read file in chunks
        i = 0
        while True:
            lines = list(islice(f, args.batch_size))
            if not lines:
                break
            if args.use_sqs:
                total_lines += send_sqs(i, lines, queues, args.batch_size)
            else:
                total_lines += send_lamda(i, lines, funcs, args.batch_size)
            i += 1
    return total_lines


def parse_range(args, queues, funcs):
    total_lines = 0
    first = 1
    if "-" in args.range:
        first = int(args.range.split("-")[0])
        final = int(args.range.split("-")[1])
    else:
        final = int(args.range)

    start = first
    while True:
        stop = min(final, start + args.batch_size)
        lines = [str(i) for i in range(start, stop + 1)]
        if args.use_sqs:
            total_lines += send_sqs(start, lines, queues, args.batch_size)
        else:
            total_lines += send_lamda(start, lines, funcs, args.batch_size)

        if stop >= final:
            break

        start += args.batch_size
    return total_lines


def get_configs():
    proc = subprocess.run(["terraform", "output", "--json"], capture_output=True)
    config_json = proc.stdout.decode()
    return json.loads(config_json)["config"]["value"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Send messages to SQS queue")
    parser.add_argument(
        "url_config", help="path to URL config JSON detailing ULS, headers, etc"
    )
    parser.add_argument(
        "--use-input-sqs",
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
    input_type = parser.add_mutually_exclusive_group(required=True)
    input_type.add_argument(
        "--range", "-r", help="Range counter, either a number or a range like 1-10"
    )
    input_type.add_argument(
        "--input-file", "-i", dest="input", help="Input file to use"
    )

    do_output = parser.add_mutually_exclusive_group(required=False)
    do_output.add_argument(
        "--output",
        "-o",
        action="store_true",
        dest="output_stdout",
        help="Also automatically call 'get_data', print to stdout out",
    )
    do_output.add_argument(
        "--output-file",
        "-of",
        dest="output_file",
        help="Also automatically call 'get_data', print to stdout and output to this file",
    )
    parser.add_argument(
        "--output-pretty",
        "-op",
        action="store_true",
        dest="pretty",
        help="If calling 'get_data', pretty print output",
    )
    parser.add_argument(
        "--output-unique-only",
        "-ou",
        dest="unique_only",
        help="If calling 'get_data', only print unique responses",
    )
    args = parser.parse_args()

    # Parse config to extract queues
    configs = get_configs()

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

    if args.input:
        total_lines = parse_file(args, queues, funcs)
    else:
        total_lines = parse_range(args, queues, funcs)

    if args.output_stdout or args.output_file or args.pretty or args.unique_only:
        # Call 
        args.expected_count = total_lines
        get_data(args, configs)
