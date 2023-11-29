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

module "amazon_s3_glue" {
  source           = "./modules/terraform-amazon-s3"
  bucket_base_name = "alcon-workshop-glue-code"
  s3_object_name   = "glue_enriched.py"
}

# Adding lambda for both raw and trusted layers
module "aws_lambda_raw" {
  source            = "./modules/terraform-aws-lambda"
  s3_bucket_arn     = module.amazon_s3_data.bucket_arn
  s3_bucket_name    = module.amazon_s3_data.bucket_name
  handler           = "src.jobs.lambda_raw.main"
  state_machine_arn = module.aws_sfn_state_machine.sfn_arn
  temp_dir          = ""
  zip_location      = "${path.module}/dist/lambda_code.zip"
  layer             = "raw"
  runtime           = "python3.9"
  timeout           = 180 # In seconds
}

module "aws_lambda_trusted" {
  source            = "./modules/terraform-aws-lambda"
  s3_bucket_arn     = module.amazon_s3_data.bucket_arn
  s3_bucket_name    = module.amazon_s3_data.bucket_name
  handler           = "src.jobs.lambda_trusted.main"
  state_machine_arn = module.aws_sfn_state_machine.sfn_arn
  temp_dir          = ""
  zip_location      = "${path.module}/dist/lambda_code.zip"
  layer             = "trusted"
  runtime           = "python3.9"
  timeout           = 180 # In seconds
}

# Adding glue job for enrichment layer
module "aws_glue" {
  source                    = "./modules/terraform-aws-glue"
  script_location           = "s3://${module.amazon_s3_glue.bucket_name}/${module.amazon_s3_glue.glue_script_name}"
  temp_dir                  = var.job_temp_dir
  arguments = {
    "--S3_BUCKET_NAME" = module.amazon_s3_data.bucket_name,
  }
  s3_glue_code_bucket_arn   = module.amazon_s3_glue.bucket_arn
  s3_glue_code_bucket_name  = module.amazon_s3_glue.bucket_name
  s3_data_bucket_arn        = module.amazon_s3_data.bucket_arn
  s3_data_bucket_name       = module.amazon_s3_data.bucket_name
}

# Adding step function (Our main workflow)
module "aws_sfn_state_machine" {
  source              = "./modules/terraform-aws-step-function"
  glue_job_arn        = module.aws_glue.glue_job_arn_python_shell
  glue_job_name       = module.aws_glue.glue_job_name_python_shell
  lambda_raw_arn      = module.aws_lambda_raw.lambda_arn
  lambda_raw_name     = module.aws_lambda_raw.lambda_name
  lambda_trusted_arn  = module.aws_lambda_trusted.lambda_arn
  lambda_trusted_name = module.aws_lambda_trusted.lambda_name
  s3_data_bucket_name = module.amazon_s3_data.bucket_name
}

# Adding CloudWatch event to trigger the step function
module "aws_cloudwatch_event" {
  source            = "./modules/terraform-aws-cloudwatch"
  sfn_function_arn  = module.aws_sfn_state_machine.sfn_arn
  sfn_function_name = module.aws_sfn_state_machine.sfn_name
}

# Adding Athena module
module "athena" {
  source = "./modules/terraform-aws-athena"
  database_name = "workshop_db"
  table_name = "workshop_table"
  s3_location = "s3://${module.amazon_s3_data.bucket_name}/enriched/"
}


# Outputs (Optional)
output "aws_s3_data_bucket_arn" {
  value = module.amazon_s3_data.bucket_arn
}

output "aws_s3_glue_code_bucket_name" {
  value = module.amazon_s3_glue.bucket_name
}

output "aws_cloudwatch_event_rule_arn" {
  value = module.aws_cloudwatch_event.aws_cloudwatch_event_rule_arn
}

output "aws_step_function_arn" {
  value = module.aws_sfn_state_machine.sfn_role_arn
}

output "aws_glue_job_arn" {
  value = module.aws_glue.glue_job_arn_python_shell
}

output "aws_lambda_raw_arn" {
  value = module.aws_lambda_raw.lambda_arn
}

output "aws_lambda_trusted_arn" {
  value = module.aws_lambda_trusted.lambda_arn
}
