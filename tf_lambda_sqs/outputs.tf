# Output details
locals {
  config = {
    aws_region    = data.aws_region.current.name
    lambda_funcs  = aws_lambda_function.tf_lambda[*].id
    queue_in_url  = var.enable_input_queue ? aws_sqs_queue.tf_queue_in[0].url : ""
    queue_out_url = aws_sqs_queue.tf_queue_out.url
  }
}

output "config" {
  value = local.config
}
