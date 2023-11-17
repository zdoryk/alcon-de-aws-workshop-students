locals {
  default_arguments = {
    "--job-language"        = var.language
    "--job-bookmark-option" = lookup(var.bookmark_options, var.bookmark)
    "--TempDir"             = "s3://${var.s3_glue_code_bucket_name}/tmp/"
    "library-set"           = "analytics"     # This is new with Python 3.9 and add packages to the runtime env.
    "--enable-continuous-cloudwatch-log" = "true"
  }
}
# IAM policies to allow access to the S3 bucket
data "aws_iam_policy_document" "policy_document" {
  statement {
    effect = "Allow"
    actions = [
      "s3:ListBucket"
    ]
    resources = [
      var.s3_data_bucket_arn,
      var.s3_glue_code_bucket_arn
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "${var.s3_data_bucket_arn}/*",
      "${var.s3_glue_code_bucket_arn}/*"
    ]
  }
}

resource "aws_iam_policy" "s3_access_iam_policy" {
  name = "sample-glue-s3-access-policy"
  policy = data.aws_iam_policy_document.policy_document.json
}

# Glue IAM roles and Policies
resource "aws_iam_role" "sample_glue_role" {
  name = "sample-glue-role"
  assume_role_policy = <<EOF
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Action":"sts:AssumeRole",
         "Principal":{
            "Service":[
               "glue.amazonaws.com"
            ]
         },
         "Effect":"Allow",
         "Sid":""
      }
   ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "glue_service_policy" {
  role       = aws_iam_role.sample_glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy_attachment" "platform_metrics_glue_iam_policy" {
  role       = aws_iam_role.sample_glue_role.name
  policy_arn = aws_iam_policy.s3_access_iam_policy.arn
}

resource "aws_glue_job" "glue_job_python_shell" {
  count = var.create ? 1 : 0

  name         = "sample-glue-job-python-shell-terraform"
  description  = "AWS Glue Python Shell Job terraform example"
  role_arn     = aws_iam_role.sample_glue_role.arn
  glue_version = "1.0"

  command {
    name           = "pythonshell"
    python_version = "3.9"
    script_location = var.script_location
  }

  default_arguments = merge(local.default_arguments, var.arguments)
  max_retries       = var.max_retries
  timeout           = var.timeout

  execution_property {
    max_concurrent_runs = var.max_concurrent
  }
}

# Outputs
output "glue_job_name_python_shell" {
  value = join(",", aws_glue_job.glue_job_python_shell.*.name)
}
output "glue_job_arn_python_shell" {
  value = join(",", aws_glue_job.glue_job_python_shell.*.arn)
}

