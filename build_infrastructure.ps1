# Set the path var
$path = Get-Location

# if there is no dist dir - create it
if (-not (Test-Path "$path\dist")) {
    New-Item -ItemType Directory -Path "$path\dist" | Out-Null
}

# Build .zip for AWS Lambda and copy Glue job script to dist
Compress-Archive -Path "$path\src" -DestinationPath "$path\dist\lambda_code.zip" -Force
Copy-Item "$path\src\jobs\glue_enriched.py" -Destination "$path\dist\glue_enriched.py" -Force

# Terraform
# If there is no .terraform dir - init terraform
if (-not (Test-Path "$path\.terraform")) {
    terraform init
}

# Destroy all the resources and apply the new ones
# terraform destroy -auto-approve
terraform plan -out "$path\dist\plan.out"
terraform apply "$path\dist\plan.out"
