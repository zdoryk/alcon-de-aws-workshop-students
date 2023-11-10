# variables
variable "glue_job_arn" {}
variable "glue_job_name" {}
variable "glue_message" {default = "This is a message passed by the AWS Step Function"}

variable "lambda_raw_arn" {}
variable "lambda_raw_name" {}

variable "lambda_trusted_arn" {}
variable "lambda_trusted_name" {}