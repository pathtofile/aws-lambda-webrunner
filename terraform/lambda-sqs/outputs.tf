# Output details
locals {
  config = {
    aws_region    = data.aws_region.current.name
    lambda_funcs  = aws_lambda_function.tf_lambda[*].id
    queue_in_url  = aws_sqs_queue.tf_queue_in.url
    queue_out_url = aws_sqs_queue.tf_queue_out.url
  }
}

output "config" {
  value = local.config
}
