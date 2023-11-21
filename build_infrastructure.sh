# Set the path var
# shellcheck disable=SC2034
path=$(pwd)

# if there is no dist dir - create it
if [ ! -d "$path"/dist ]; then
  mkdir "$path"/dist
fi
# Build .zip for AWS Lambda and copy Glue job script to dist
zip -r "$path"/dist/lambda_code.zip src
cp "$path"/src/jobs/glue_enriched.py "$path"/dist/glue_enriched.py

# Terraform
# If there is no .terraform dir - init terraform
# shellcheck disable=SC2164
if [ ! -d "$path"/.terraform ]; then
  terraform init
fi

# Destroy all the resources and apply the new ones
#terraform destroy -auto-approve
terraform plan -out dist/plan.out
terraform apply dist/plan.out
