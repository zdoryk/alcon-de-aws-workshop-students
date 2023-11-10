# terraform and AWS configurations
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
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
  source = "./modules/terraform-amazon-s3"
  bucket_base_name = "alcon-workshop-data"
  s3_object_name = "lambda_code.zip"
}

module "amazon_s3_glue" {
  source = "./modules/terraform-amazon-s3"
  bucket_base_name = "alcon-workshop-glue-code"
  s3_object_name = "glue_script.py"
}

# Adding lambda for both raw and trusted layers
module "aws_lambda_raw" {
  source = "./modules/terraform-aws-lambda"
  s3_bucket_arn = module.amazon_s3_data.bucket_arn
  s3_bucket_name = module.amazon_s3_data.bucket_name
  handler = "src.jobs.lambda_raw.main"
  state_machine_arn = module.aws_sfn_state_machine.sfn_arn
  temp_dir = ""
  zip_location = "${path.module}/dist/lambda_code.zip"
  layer = "raw"
  runtime = "python3.9"
  timeout = 180 # In seconds
}

module "aws_lambda_trusted" {
  source = "./modules/terraform-aws-lambda"
  s3_bucket_arn = module.amazon_s3_data.bucket_arn
  s3_bucket_name = module.amazon_s3_data.bucket_name
  handler = "src.jobs.lambda_trusted.main"
  state_machine_arn = module.aws_sfn_state_machine.sfn_arn
  temp_dir = ""
  zip_location = "${path.module}/dist/lambda_code.zip"
  layer = "trusted"
  runtime = "python3.9"
  timeout = 180 # In seconds
}

# Adding glue job for enrichment layer
module "aws_glue" {
  source          = "./modules/terraform-aws-glue"
  script_location = "s3://${module.amazon_s3_glue.bucket_name}/${module.amazon_s3_glue.glue_script_name}"
  temp_dir        = var.job_temp_dir
  s3_glue_code_bucket_arn   = module.amazon_s3_glue.bucket_arn
  s3_glue_code_bucket_name  = module.amazon_s3_glue.bucket_name
  s3_data_bucket_arn        = module.amazon_s3_data.bucket_arn
  s3_data_bucket_name       = module.amazon_s3_data.bucket_name
}

# Adding step function (Our main workflow)
module "aws_sfn_state_machine" {
  source        = "./modules/terraform-aws-step-function"
  glue_job_arn  = module.aws_glue.glue_job_arn
  glue_job_name = module.aws_glue.glue_job_name
  lambda_raw_arn = module.aws_lambda_raw.lambda_arn
  lambda_raw_name = module.aws_lambda_raw.lambda_name
  lambda_trusted_arn = module.aws_lambda_trusted.lambda_arn
  lambda_trusted_name = module.aws_lambda_trusted.lambda_name
}

# Adding CloudWatch event to trigger the step function
module "aws_cloudwatch_event" {
  source            = "./modules/terraform-aws-cloudwatch"
  sfn_function_arn  = module.aws_sfn_state_machine.sfn_arn
  sfn_function_name = module.aws_sfn_state_machine.sfn_name
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
  value = module.aws_glue.glue_job_arn
}

output "aws_lambda_raw_arn" {
  value = module.aws_lambda_raw.lambda_arn
}

output "aws_lambda_trusted_arn" {
  value = module.aws_lambda_trusted.lambda_arn
}



## Only create the S3 bucket if it doesn't exist
#resource "aws_s3_bucket" "alcon-workshop-s3-bucket" {
#  bucket = "alcon-workshop-s3-bucket"
#}
#
#
## Lambda IAM role creation
#resource "aws_iam_role" "alcon-workshop-lambda_role" {
#  name = "alcon-workshop-lambda_role"
#  assume_role_policy = jsonencode({
#    Version = "2012-10-17",
#    Statement = [
#      {
#        Action = "sts:AssumeRole",
#        Effect = "Allow",
#        Principal = {
#          Service = "lambda.amazonaws.com"
#        }
#      }
#    ]
#  })
#}
#
#
## Lambda creation
#resource "aws_lambda_function" "alcon-workshop-lambda" {
#  function_name = "alcon-workshop-lambda-raw"
#  handler = "src.jobs.lambda_raw.handler"
#  runtime = "python3.9"
#  role = aws_iam_role.alcon-workshop-lambda_role.arn
#  /*
#  NOTE: ${path.module} is a special Terraform interpolation function that returns the filesystem path of the directory
#        where the currently executing Terraform configuration files are located. It's a convenient way to reference files
#        or directories relative to your Terraform configuration, regardless of where your Terraform code is located.
#  */
#  source_code_hash = filebase64sha256("${path.module}/../dist/lambda_code.zip")
#  filename = "${path.module}/../dist/lambda_code.zip"
#
#  environment {
#    variables = {
#      S3_BUCKET_NAME = aws_s3_bucket.alcon-workshop-s3-bucket.bucket
#    }
#  }
#}
#
## Glue Catalog creation
## DB
#resource "aws_glue_catalog_database" "alcon-workshop-glue_db" {
#  name = "alcon-workshop-glue_db"
#}
#
## Table on enriched bucket
#resource "aws_glue_catalog_table" "alcon-workshop-glue_table" {
#  name    = "alcon-workshop-glue_table"
#  database_name = aws_glue_catalog_database.alcon-workshop-glue_db.name
#  table_type    = "EXTERNAL_TABLE"
#  parameters = {
#    "classification" = "parquet"
#  }
#  storage_descriptor {
#    location = "s3://${aws_s3_bucket.alcon-workshop-s3-bucket.bucket}/enriched"
#  }
#}
#
#resource "aws_iam_role" "glue_job_role" {
#  name = "GlueJobRole"
#
#  assume_role_policy = jsonencode({
#    Version = "2012-10-17",
#    Statement = [
#      {
#        Action = "sts:AssumeRole",
#        Effect = "Allow",
#        Principal = {
#          Service = "glue.amazonaws.com"  # Glue service
#        }
#      }
#    ]
#  })
#}
#
#resource "aws_iam_role_policy_attachment" "glue_job_s3_access" {
#  role       = aws_iam_role.glue_job_role.name
#  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"  # AmazonS3FullAccess policy
#}
#
#
## Glue Job creation
#resource "aws_glue_job" "alcon-workshop-glue_job" {
#  name          = "alcon-workshop-glue_job"
#  role_arn      = aws_iam_role.glue_job_role.arn  # Use the IAM role for the Glue job
#  glue_version = "4.0"
#  command {
#    name = "glueetl"
#    python_version = "3"
#    /*
#      AWS Glue jobs require the ETL (Extract, Transform, Load) script to be stored in an Amazon S3 location, and it doesn't
#      support running ETL scripts directly from a local machine or other file storage locations. The script needs
#      to be accessible from an S3 path or an AWS Glue Data Catalog table.
#    */
##    script_location = "s3://${aws_s3_bucket.alcon-workshop-s3-bucket.bucket}/path-to-your-Glue-job-script"
#    script_location = "s3://alcon-de-aws-workshop-2023/lambda_raw.py"
#  }
#}
#
#
#resource "aws_iam_role" "step_function_role" {
#  name = "StepFunctionRole"
#
#  assume_role_policy = jsonencode({
#    Version = "2012-10-17",
#    Statement = [
#      {
#        Action = "sts:AssumeRole",
#        Effect = "Allow",
#        Principal = {
#          Service = "states.amazonaws.com"  # Step Functions service
#        }
#      }
#    ]
#  })
#}
#resource "aws_iam_policy" "step_function_policy" {
#  name        = "StepFunctionPolicy"
#  description = "IAM policy for Step Function with Lambdas and Glue Job"
#
#  policy = jsonencode({
#    Version = "2012-10-17",
#    Statement = [
#      {
#        Effect = "Allow",
#        Action = [
#          "lambda:InvokeFunction",
#          "glue:StartJobRun",
#          "states:StartExecution"
#        ],
#        Resource = "*"
#      }
#    ]
#  })
#}
#
#resource "aws_iam_role_policy_attachment" "step_function_policy_attachment" {
#  role       = aws_iam_role.step_function_role.name
#  policy_arn = aws_iam_policy.step_function_policy.arn
#}
#
## Step Function creation (Our main workflow)
#resource "aws_sfn_state_machine" "alcon-workshop-sfn" {
#  name     = "alcon-workshop-sfn"
#  role_arn = aws_iam_role.step_function_role.arn  # Use the IAM role for Step Function
#
#
#  definition = jsonencode({
#    "Comment": "An example of the Amazon States Language using a choice state.",
#    StartAt = "GlueJob",
##    StartAt = "LambdaFunction",
#    States = {
##      LambdaFunction = {
##        Type = "Task",
##        Resource = aws_lambda_function.alcon-workshop-lambda.arn,
###        End = true
##        Next = "GlueJob"  # Name of the next state, not the resource name
##      },
#      GlueJob = {
#        Type = "Task",
#        Resource = aws_glue_job.alcon-workshop-glue_job.arn,
#        End = true
#      }
#    }
#  })
#}
