# SQS Queues
resource "aws_sqs_queue" "tf_queue_in" {
  name = "dothingi-in"
}
resource "aws_sqs_queue" "tf_queue_out" {
  name = "dothingi-out"
}
