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
  bucket = "dothingi-${data.aws_region.current.name}"
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



variable "lambda_count" { default = 5 }

resource "aws_lambda_function" "tf_lambda" {
  count         = var.lambda_count
  function_name = "dothingi_${count.index}"
  role          = aws_iam_role.tf_role.arn
  runtime       = "python3.9"
  handler       = "lambda.lambda_handler"
  timeout       = 5 # Seconds
  memory_size   = 128
  s3_bucket     = aws_s3_bucket.tf_bucket.id
  s3_key        = aws_s3_object.tf_bucket_object.id
  # filename      = "${path.module}/lambda.zip"

  environment {
    variables = {
      ResponseQueueURL = aws_sqs_queue.tf_queue_out.url
      LambdaName       = "dothingi_${count.index}"
    }
  }

  # We first must create the ZIP to upload
  depends_on = [null_resource.create_lambda_zip]
}


# Lambda-SQS Event Source mapping
# resource "aws_lambda_event_source_mapping" "example" {
#   count            = var.lambda_count
#   event_source_arn = aws_sqs_queue.tf_queue_in.arn
#   function_name    = aws_lambda_function.tf_lambda[count.index].arn
#   batch_size       = 1
# }
