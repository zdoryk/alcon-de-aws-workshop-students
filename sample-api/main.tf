terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  profile = "default"
  region  = "us-east-1"
}


module "amazon_s3_data" {
  source           = "./modules/s3"
  bucket_base_name = "5-min-refresh-data"
}

module "aws_lambda_gateway" {
  source         = "./modules/api-gateway-lambda"
  source_dir     = "${path.module}/src"
  output_path    = "${path.module}/dist/lambda_code.zip"
  runtime        = "python3.9"
  handler        = "gateway.lambda_handler"
  s3_bucket_arn  = module.amazon_s3_data.bucket_arn
  s3_bucket_name = module.amazon_s3_data.bucket_name
  timeout        = 180 # In seconds
}

# Adding lambda for both raw and trusted layers
module "aws_lambda_generate" {
  source         = "./modules/lambda-generate"
  s3_bucket_arn  = module.amazon_s3_data.bucket_arn
  s3_bucket_name = module.amazon_s3_data.bucket_name
  handler        = "generate_data.lambda_handler"
#  state_machine_arn = module.aws_sfn_state_machine.sfn_arn
  zip_location   = "${path.module}/dist/lambda_code.zip"
  runtime        = "python3.9"
  timeout        = 180 # In seconds
}

module "cloud_watch" {
  source               = "./modules/cloudwatch_trigger"
  lambda_function_arn  = module.aws_lambda_generate.lambda_arn
  lambda_function_name = module.aws_lambda_generate.lambda_name
}
