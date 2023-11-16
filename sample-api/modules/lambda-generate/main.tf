data "aws_region" "current" {}
data "aws_caller_identity" "current" {}


# Lambda IAM role creation
resource "aws_iam_role" "lambda_generate_data_role" {
  name = "lambda_generate_data_role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_policy" "lambda_generate_data_policy" {
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action": [
          "logs:*"
        ],
        "Resource": "arn:aws:logs:*:*:*",
        "Effect": "Allow"
      },
      {
        "Action": [
          "s3:PutObject"
        ],
        "Resource": [var.s3_bucket_arn, "${var.s3_bucket_arn}/*"],  # Replace "your-bucket-name" with your actual S3 bucket name
        "Effect": "Allow"
      },
    ]
  })
}


# Attach the IAM policies to the equivalent rule
resource "aws_iam_role_policy_attachment" "lambda_generate_data_role_policy_attachment" {
  role       = aws_iam_role.lambda_generate_data_role.name
  policy_arn = aws_iam_policy.lambda_generate_data_policy.arn
}

# Lambda creation
resource "aws_lambda_function" "lambda_generate_data" {
  function_name    = "lambda-data"
  handler          = var.handler
  runtime          = var.runtime
  role             = aws_iam_role.lambda_generate_data_role.arn
  source_code_hash = filebase64sha256(var.zip_location)
  filename         = var.zip_location
  timeout          = var.timeout
  layers           = ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:10"]
  environment {
    variables = {
      BUCKET_NAME = var.s3_bucket_name,
    }
  }
}

output "lambda_arn" {
  value = aws_lambda_function.lambda_generate_data.arn
}

output "lambda_name" {
  value = aws_lambda_function.lambda_generate_data.function_name
}