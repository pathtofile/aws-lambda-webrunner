# SQS Queues
resource "aws_sqs_queue" "tf_queue_in" {
  name = "dothingi-in"
}
resource "aws_sqs_queue" "tf_queue_out" {
  name = "dothingi-out"
}


# Output Queue URLs to send and recieve messages from
output "queue_in" {
  value = aws_sqs_queue.tf_queue_in.url
}

output "queue_out" {
  value = aws_sqs_queue.tf_queue_out.url
}
