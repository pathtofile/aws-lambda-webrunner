# Role and Policy to allow Lambda to send and recieve
# SQS messages
resource "aws_iam_role" "tf_role" {
  name               = "dothingi-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": { "Service": "lambda.amazonaws.com" }
    }
  ]
}
EOF
}

resource "aws_iam_policy" "tf_policy" {
  name   = "dothingi-policy"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:SendMessage",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "tf_role_policy" {
  role       = aws_iam_role.tf_role.name
  policy_arn = aws_iam_policy.tf_policy.arn
}
