import argparse
import json
import time
import boto3

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Recieve messages from SQS queues")
    parser.add_argument("config", help="path to 'terraform output --json' config JSON")
    parser.add_argument("--print", "-p", action="store_true", help="Print each message response")
    args = parser.parse_args()

    # Parse config to extract queues
    with open(args.config, "r") as f:
        config = json.load(f)
    queues = list()
    for q in config["queue_out_url"]["value"]:
        queues.append(boto3.resource("sqs", region_name=q["region"]).Queue(q["url"]))

    unique_ips = []
    try:
        while True:
            for queue in queues:
                messages_to_delete = []
                messages = queue.receive_messages(
                    MaxNumberOfMessages=10, WaitTimeSeconds=1
                )
                for i, message in enumerate(messages):
                    body = message.body
                    if args.print:
                        print(body)
                    ip_address = body.split(" | ")[-1]
                    if ip_address not in unique_ips:
                        unique_ips.append(ip_address)
                        print(f"[*] {len(unique_ips)} | {ip_address}")
                    messages_to_delete.append(
                        {"Id": f"id-{i}", "ReceiptHandle": message.receipt_handle}
                    )

                # Remove messages from queue
                if len(messages_to_delete) > 0:
                    queue.delete_messages(Entries=messages_to_delete)
            if len(messages) > 0:
                print(f"[{len(messages):02}] .")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    print("------------------")
    print(f"Unique IPs: {len(unique_ips)}")
    print("\n".join(unique_ips))
