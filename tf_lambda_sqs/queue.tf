# SQS Queues
# Only privion input queue in required
resource "aws_sqs_queue" "tf_queue_in" {
  count                      = var.enable_input_queue ? 1 : 0
  visibility_timeout_seconds = var.lambda_timeout_seconds
  name                       = "${var.base_name}-in"
}

resource "aws_sqs_queue" "tf_queue_out" {
  name = "${var.base_name}-out"
}
