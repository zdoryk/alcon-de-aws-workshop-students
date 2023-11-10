# AWS Step Functions IAM roles and Policies
resource "aws_iam_role" "aws_sfn_role" {
  name = "aws-sfn-role"
  assume_role_policy = <<EOF
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Action":"sts:AssumeRole",
         "Principal":{
            "Service":[
                "states.amazonaws.com"
            ]
         },
         "Effect":"Allow",
         "Sid":"StepFunctionAssumeRole"
      }
   ]
}
EOF
}

resource "aws_iam_role_policy" "step_function_policy" {
  name = "aws-sfn-policy"
  role    = aws_iam_role.aws_sfn_role.id

  policy  = <<EOF
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Action":[
                "glue:StartJobRun",
                "glue:GetJobRun",
                "glue:GetJobRuns",
                "glue:BatchStopJobRun"
         ],
         "Effect":"Allow",
         "Resource":"${var.glue_job_arn}"
      },
      {
        "Action": [
          "lambda:InvokeFunction",
          "lambda:GetFunction",
          "lambda:ListFunctions"
        ],
        "Effect": "Allow",
        "Resource": [
          "${var.lambda_raw_arn}",
          "${var.lambda_trusted_arn}"
        ]
      }
  ]
}

EOF
}

# AWS Step function definition
resource "aws_sfn_state_machine" "aws_step_function_workflow" {
  name = "aws-step-function-workflow"
  role_arn = aws_iam_role.aws_sfn_role.arn
  definition = jsonencode({
    "Comment":"A description of the sample glue job state machine using Terraform",
    "StartAt":"Lambda Raw",
    "States":{
      "Lambda Raw":{
        Type = "Task",
        Resource = var.lambda_raw_arn,
        Next = "Lambda Trusted"  # Name of the next state, not the resource name
      },
      "Lambda Trusted":{
        Type = "Task",
        Resource = var.lambda_trusted_arn,
        Next = "Glue Enriched"  # Name of the next state, not the resource name
      },
      "Glue Enriched":{
        "Type":"Task",
        "Resource":"arn:aws:states:::glue:startJobRun.sync",
        "Parameters":{
          "JobName":var.glue_job_name,
          "Arguments": {
            "--message": var.glue_message
          }
        },
        "End":true
      }
    }
  })
}


# outputs
output "sfn_role_arn" {
  value = aws_iam_role.aws_sfn_role.arn
}
output "sfn_name" {
  value = aws_sfn_state_machine.aws_step_function_workflow
}
output "sfn_arn" {
  value = aws_sfn_state_machine.aws_step_function_workflow.arn
}