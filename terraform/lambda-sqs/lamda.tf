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

# Add ZIP to S3
resource "aws_s3_bucket" "tf_bucket" {
  bucket = "${var.base_name}-${data.aws_region.current.name}"
}
resource "aws_s3_bucket_acl" "tf_bucket_acl" {
  bucket = aws_s3_bucket.tf_bucket.id
  acl    = "private"
}
resource "aws_s3_object" "tf_bucket_object" {
  bucket = aws_s3_bucket.tf_bucket.id
  key    = "lambda_zip"
  source = "${path.module}/lambda.zip"

  # We first must create the ZIP to upload
  depends_on = [null_resource.create_lambda_zip]
}

resource "aws_lambda_function" "tf_lambda" {
  count         = var.lambda_count
  function_name = "${var.base_name}-${count.index}"
  role          = aws_iam_role.tf_role.arn
  runtime       = "python3.9"
  handler       = "lambda.lambda_handler"
  timeout       = var.lambda_timeout_seconds
  memory_size   = var.lambda_memory_size
  s3_bucket     = aws_s3_bucket.tf_bucket.id
  s3_key        = aws_s3_object.tf_bucket_object.id

  environment {
    variables = {
      ResponseQueueURL = aws_sqs_queue.tf_queue_out.url
      LambdaName       = "${var.base_name}-${count.index}"
    }
  }

  # We first must create the ZIP to upload
  depends_on = [null_resource.create_lambda_zip]
}


# Link the input Queue to one of the lambdas
resource "aws_lambda_event_source_mapping" "example" {
  count = var.enable_input_queue ? var.lambda_count : 0

  event_source_arn = aws_sqs_queue.tf_queue_in[0].arn
  function_name    = aws_lambda_function.tf_lambda[count.index].arn
  batch_size       = 10
}
