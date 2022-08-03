from contextlib import ExitStack
import argparse
import json
import subprocess
import time
import boto3

UNIQUE_DATA = []

def log_data(data, line, json_response, outf, pretty):
    if json_response:
        data = json.loads(data)
    if pretty:
        output = json.dumps(
            {
                "line": line,
                "data": data,
            },
            indent=True,
        )
    else:
        output = json.dumps(
            {
                "line": line,
                "data": data,
            }
        )

    print(output)
    if outf:
        outf.write(f"{output}\n")
        outf.flush()


def recieve_queues(args, queues, outf):
    global UNIQUE_DATA
    message_count = 0
    for queue in queues:
        messages_to_delete = []
        messages = queue.receive_messages(
            MaxNumberOfMessages=args.batch_size, WaitTimeSeconds=1
        )
        message_count += len(messages)
        for i, message in enumerate(messages):
            resp = json.loads(message.body)
            data = resp["data"]
            line = resp["line"]
            json_response = resp["json_response"]
            if args.unique_only:
                if data not in UNIQUE_DATA:
                    log_data(data, line, json_response, outf, args.pretty)
                    UNIQUE_DATA.append(data)
            else:
                log_data(data, line, json_response, outf, args.pretty)

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
    return message_count


def get_configs():
    proc = subprocess.run(["terraform", "output", "--json"], capture_output=True)
    config_json = proc.stdout.decode()
    return json.loads(config_json)["config"]["value"]


def get_data(args, configs):
    queues = []
    for c in configs:
        sqs = boto3.resource("sqs", region_name=c["aws_region"])
        queues.append(sqs.Queue(c["queue_out_url"]))

    try:
        with ExitStack():
            outf = open(args.output_file, "w", encoding="utf-8") if args.output_file else None
            total_messages = 0
            while True:
                total_messages += recieve_queues(args, queues, outf)
                if args.expected_count > 0 and total_messages >= args.expected_count:
                    break
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Recieve messages from SQS queues")
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
        "--output-file",
        "-f",
        dest="output_file",
        help="Optional output file to stream to",
    )
    parser.add_argument(
        "--pretty",
        "-p",
        help="Prettify output",
        action="store_true",
    )
    parser.add_argument(
        "--expected-count",
        "-e",
        dest="expected_count",
        default=0,
        type=int,
        help="Expected number of responses, if known",
    )
    args = parser.parse_args()

    # Parse config to extract queues
    configs = get_configs()

    get_data(args, configs)
