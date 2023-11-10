# Set the path var
# shellcheck disable=SC2034
path=$(pwd)

# if there is no dist dir - create it
if [ ! -d "$path"/dist ]; then
  mkdir "$path"/dist
fi
# Build .zip for AWS Lambda
zip -r "$path"/dist/lambda_code.zip src
cp "$path"/src/jobs/glue_enriched.py "$path"/dist/glue_enriched.py

#TODO: Add Glue files

# Terraform
# shellcheck disable=SC2164
if [ ! -d "$path"/.terraform ]; then
  terraform init
fi
# if terraform state list | grep s3 bucket - remove it
#if terraform state list | grep s3; then
#  terraform state rm aws_s3_bucket.alcon-workshop-s3-bucket
#fi
#terraform state rm aws_s3_bucket.alcon-workshop-s3-bucket
terraform destroy -auto-approve
terraform plan -out dist/plan.out
terraform apply dist/plan.out
