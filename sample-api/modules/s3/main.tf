# Resources

## create a S3 Bucket
data "aws_caller_identity" "current_caller" {}

resource "aws_s3_bucket" "s3_sample_bucket" {
  bucket = "${var.bucket_base_name}-${data.aws_caller_identity.current_caller.id}"
}

## block public access
resource "aws_s3_bucket_public_access_block" "s3_bucket_block_public_access" {
  bucket = aws_s3_bucket.s3_sample_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


# Outputs
output "bucket_name" {
  value = aws_s3_bucket.s3_sample_bucket.bucket
}
output "bucket_arn" {
  value = aws_s3_bucket.s3_sample_bucket.arn
}
