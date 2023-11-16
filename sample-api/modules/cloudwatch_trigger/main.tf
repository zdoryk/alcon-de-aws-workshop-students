locals{
  schedule_expression= "rate(5 minutes)"
}

# Variables
variable "lambda_function_name" {}
variable "lambda_function_arn" {}

# Resources

data "aws_iam_policy_document" "allow_cloudwatch_to_execute_policy" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type = "Service"
      identifiers = [
        "states.amazonaws.com",
        "events.amazonaws.com"
      ]
    }
  }
}

resource "aws_iam_role" "allow_cloudwatch_to_execute_role" {
  name               = "aws-events-invoke-lambda"
  assume_role_policy = data.aws_iam_policy_document.allow_cloudwatch_to_execute_policy.json
}

resource "aws_iam_role_policy" "lambda_execution" {
  name        = "lambda_execution_policy"
  role   = aws_iam_role.allow_cloudwatch_to_execute_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Effect": "Allow",
      "Resource": "${var.lambda_function_arn}"
    }
  ]
}
EOF
}

resource "aws_cloudwatch_event_rule" "every_five_minutes" {
    name                = "every-five-minutes"
    description         = "Fires every five minutes"
    schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "check_foo_every_five_minutes" {
    rule      = aws_cloudwatch_event_rule.every_five_minutes.name
    target_id = "check_foo"
    arn       = var.lambda_function_arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
    statement_id  = "AllowExecutionFromCloudWatch"
    action        = "lambda:InvokeFunction"
    function_name = var.lambda_function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.every_five_minutes.arn
}

# Outputs
#output "aws_cloudwatch_event_rule_arn" {
#  value = aws_cloudwatch_event_rule.sfn_trigger_rule.arn
#}