# AWS Lambda to handle messages
resource "null_resource" "create_lambda_zip" {
  provisioner "local-exec" {
    command = "python ${path.module}/scripts/zip_create.py ${path.module}/../../lambda/lambda.py ${path.module}/lambda.zip"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "python ${path.module}/scripts/delete_file.py ${path.module}/lambda.zip"
  }
}

resource "aws_lambda_function" "tf_lambda" {
  function_name = "dothingi"
  role          = aws_iam_role.tf_role.arn
  runtime       = "python3.9"
  filename      = "${path.module}/lambda.zip"
  handler       = "lambda.lambda_handler"
  timeout       = 5 # Seconds
  memory_size   = 128

  environment {
    variables = {
      ResponseQueueURL = aws_sqs_queue.tf_queue_out.url
    }
  }

  # We first must create the ZIP to upload
  depends_on = [null_resource.create_lambda_zip]
}


# Lambda-SQS Event Source mapping
resource "aws_lambda_event_source_mapping" "example" {
  event_source_arn = aws_sqs_queue.tf_queue_in.arn
  function_name    = aws_lambda_function.tf_lambda.arn
  batch_size       = 1
}
