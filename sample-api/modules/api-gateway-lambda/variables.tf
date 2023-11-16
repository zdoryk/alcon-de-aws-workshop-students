variable "source_dir" {}
variable "output_path" {}

variable "runtime" {}
variable "handler" {}


variable "s3_bucket_name" {}
variable "s3_bucket_arn" {}

variable "timeout" {
  default = 60 # Seconds
}