variable "zip_location" {}

variable "max_retries" {
  default = 0
}

variable "timeout" {
  default = 60 # Seconds
}

variable "arguments" {
  type    = map(string)
  default = {}
}

variable "s3_bucket_name" {}
variable "s3_bucket_arn" {}
#variable "state_machine_arn" {}

variable "handler" {} # src.jobs.lambda_raw.handler

#variable "layer" {}
variable "runtime" {}
