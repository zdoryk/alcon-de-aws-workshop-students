# Bucket creation
resource "aws_s3_bucket" "alcon-workshop-s3_bucket" {
  bucket = "your-s3-bucket-name"
}

resource "aws_s3_bucket_acl" "alcon-workshop-s3_bucket_acl" {
  bucket = aws_s3_bucket.alcon-workshop-s3_bucket.id
  # Specify your ACL settings here
  # For example, if you want a private bucket, you can set it to "private" like this:
  acl = "private"
}


# Lambda IAM role creation
resource "aws_iam_role" "alcon-workshop-lambda_role" {
  name = "lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}


# Lambda creation
resource "aws_lambda_function" "alcon-workshop-lambda" {
  function_name = "lambda_raw"
  handler = "index.handler"
  runtime = "python3.9"
  role = aws_iam_role.alcon-workshop-lambda_role.arn
  /*
  NOTE: ${path.module} is a special Terraform interpolation function that returns the filesystem path of the directory
        where the currently executing Terraform configuration files are located. It's a convenient way to reference files
        or directories relative to your Terraform configuration, regardless of where your Terraform code is located.
  */
  source_code_hash = filebase64sha256("${path.module}/../dist/lambda_raw.zip")
  filename = "${path.module}/../dist/lambda_raw.zip"

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.alcon-workshop-s3_bucket.bucket
    }
  }
}

# Glue Catalog creation
# DB
resource "aws_glue_catalog_database" "alcon-workshop-glue_db" {
  name = "my_glue_database"
}

# Table on enriched bucket
resource "aws_glue_catalog_table" "alcon-workshop-glue_table" {
  name    = "my_glue_table"
  database_name = aws_glue_catalog_database.alcon-workshop-glue_db.name
  table_type    = "EXTERNAL_TABLE"
  parameters = {
    "classification" = "parquet"
  }
  storage_descriptor {
    location = "s3://${aws_s3_bucket.alcon-workshop-s3_bucket.bucket}/enriched"
  }
}


# Glue Job creation
resource "aws_glue_job" "alcon-workshop-glue_job" {
  name          = "my-glue-job"
  role_arn      = aws_iam_role.alcon-workshop-lambda_role.arn  # Use the same IAM role as Lambda
  command {
    name = "glueetl"
    python_version = "3"
    /*
      AWS Glue jobs require the ETL (Extract, Transform, Load) script to be stored in an Amazon S3 location, and it doesn't
      support running ETL scripts directly from a local machine or other file storage locations. The script needs
      to be accessible from an S3 path or an AWS Glue Data Catalog table.
    */
    script_location = "s3://${aws_s3_bucket.alcon-workshop-s3_bucket.bucket}/path-to-your-Glue-job-script"
  }
}

# Step Function creation (Our main workflow)
resource "aws_sfn_state_machine" "alcon-workshop-sfn" {
  name     = "my-step-function"
  role_arn = aws_iam_role.alcon-workshop-lambda_role.arn

  definition = jsonencode({
    Comment = "My Step Function",
    StartAt = "LambdaFunction",
    States = {
      LambdaFunction = {
        Type = "Task",
        Resource = aws_lambda_function.alcon-workshop-lambda.arn,
        End = false,  # Set to false to continue with the next state
        Next = "GlueJob"  # Name of the next state
      },
      GlueJob = {
        Type = "Task",
        Resource = aws_glue_job.alcon-workshop-glue_job.name,
        End = true
      }
    }
  })
}
