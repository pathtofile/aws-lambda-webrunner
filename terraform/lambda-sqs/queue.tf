# SQS Queues
resource "aws_sqs_queue" "tf_queue_in" {
  name = "dothingi-in"
}
resource "aws_sqs_queue" "tf_queue_out" {
  name = "dothingi-out"
}


# Output Queue URLs to send and recieve messages from
locals {
  in_url = {
    region = data.aws_region.current.name
    url = aws_sqs_queue.tf_queue_in.url
  }
  out_url = {
    region = data.aws_region.current.name
    url = aws_sqs_queue.tf_queue_out.url
  }
}

output "queue_in_url" {
  value = local.in_url
}

output "queue_out_url" {
  value = local.out_url
}
