variable "create" {
  default = true
}

variable "role_arn" {
  default = ""
}

variable "connections" {
  type    = list(string)
  default = []
}

variable "zip_location" {}

variable "command_name" {
  default = ""
}

variable "temp_dir" {
}

variable "description" {
  default = ""
}

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

variable "handler" {} # src.jobs.lambda_raw.handler

variable "layer" {}
variable "runtime" {}
