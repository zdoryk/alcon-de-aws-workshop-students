# Resources

## create a S3 Bucket
data "aws_caller_identity" "current_caller" {}

resource "aws_s3_bucket" "s3_sample_bucket" {
  bucket = "${var.bucket_base_name}-${data.aws_caller_identity.current_caller.id}"
}

## block public access
resource "aws_s3_bucket_public_access_block" "s3_glue_bucket_block_public_access" {
  bucket = aws_s3_bucket.s3_sample_bucket.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

# upload the AWS Glue script to the bucket
resource "aws_s3_bucket_object" "script_object" {
  bucket = aws_s3_bucket.s3_sample_bucket.bucket
  key    = var.s3_object_name
  source = "./dist/${var.s3_object_name}"
  acl = "private"
}

## IAM Resources



# Outputs
output "bucket_name" {
  value = aws_s3_bucket.s3_sample_bucket.bucket
}
output "bucket_arn" {
  value = aws_s3_bucket.s3_sample_bucket.arn
}

output "glue_script_name" {
  value = aws_s3_bucket_object.script_object.key
}