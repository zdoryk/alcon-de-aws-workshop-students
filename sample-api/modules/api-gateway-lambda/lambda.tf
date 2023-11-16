# Create IAM Role for lambda
resource "aws_iam_role" "gateway_lambda_role" {
 name   = "gateway_lambda_role"
 assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# IAM policy for the lambda
resource "aws_iam_policy" "policy_for_gateway_lambda_role" {

  name         = "policy_for_gateway_lambda_role"
  path         = "/"
  description  = "AWS IAM Policy for managing aws lambda role"
  policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
        "Action": [
          "logs:*"
        ],
        "Resource": "arn:aws:logs:*:*:*",
        "Effect": "Allow"
    },
    {
      "Effect" : "Allow",
      "Action" : [
        "lambda:InvokeFunction",
        "lambda:GetFunction"
      ],
      "Resource" : "*"
    },
    {
      "Action": [
        "s3:GetObject",
        "s3:listBucket",
      ],
      "Resource": [var.s3_bucket_arn, "${var.s3_bucket_arn}/*"],  # Replace "your-bucket-name" with your actual S3 bucket name
      "Effect": "Allow"
    },
  ]
})
}

# Role - Policy Attachment
resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
  role        = aws_iam_role.gateway_lambda_role.name
  policy_arn  = aws_iam_policy.policy_for_gateway_lambda_role.arn
}

# Zipping the code, lambda wants the code as zip file
data "archive_file" "zip_the_python_code" {
 type        = "zip"
 source_dir  = var.source_dir
 output_path = var.output_path
}

# Lambda Function, in terraform ${path.module} is the current directory.
resource "aws_lambda_function" "lambda_function" {
  filename                       = var.output_path
  function_name                  = "lambda-gateway"
  role                           = aws_iam_role.gateway_lambda_role.arn
  handler                        = var.handler
  runtime                        = var.runtime
  layers                         = ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:10"]
  depends_on                     = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
  timeout                        = var.timeout
  source_code_hash = filebase64sha256(var.output_path)
  environment {
    variables = {
      BUCKET_NAME = var.s3_bucket_name,
    }
  }
}

# With Lambda permission, API Gateway can invoke Lambda
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.example.execution_arn}/*/*"
}

