# terraform and AWS configurations
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.25"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "us-east-1"
}

# Variables
variable "job_temp_dir" {
  default = ""
}

# Modules
# Create the S3 buckets
module "amazon_s3_data" {
  source           = "./modules/terraform-amazon-s3"
  bucket_base_name = "alcon-workshop-data"
  s3_object_name   = "lambda_code.zip"
}

# Note: Only notification lambda function, data s3 bucket
# and relevant permissions are being deployed

# Adding lambda for notification layer
module "aws_lambda_notification" {
  source            = "./modules/terraform-aws-lambda"
  s3_bucket_arn     = module.amazon_s3_data.bucket_arn
  s3_bucket_name    = module.amazon_s3_data.bucket_name
  handler           = "src.jobs.lambda_notification.main"
  temp_dir          = ""
  zip_location      = "${path.module}/dist/lambda_code.zip"
  layer             = "notification"
  runtime           = "python3.9"
  timeout           = 180 # In seconds
}

# Source: https://faun.pub/building-s3-event-triggers-for-aws-lambda-using-terraform-1d61a05b4c97
# Adding S3 bucket as trigger to my lambda and giving the permissions
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = module.amazon_s3_data.bucket_name
  lambda_function {
    lambda_function_arn = module.aws_lambda_notification.lambda_arn
    events              = ["s3:ObjectCreated:*"]
  }
}

resource "aws_lambda_permission" "bucket_lambda_permission" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = module.aws_lambda_notification.lambda_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.amazon_s3_data.bucket_arn
}

# Outputs (Optional)
output "aws_s3_data_bucket_arn" {
  value = module.amazon_s3_data.bucket_arn
}

output "aws_lambda_notification_arn" {
  value = module.aws_lambda_notification.lambda_arn
}
