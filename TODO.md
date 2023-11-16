- [ ] Get aws cli to test this:

    ``` shell
    Planning failed. Terraform encountered an error while generating this plan.
    
    ╷
    │ Error: No valid credential sources found
    │ 
    │   with provider["registry.terraform.io/hashicorp/aws"],
    │   on provider.tf line 1, in provider "aws":
    │    1: provider "aws" {
    │ 
    │ Please see https://registry.terraform.io/providers/hashicorp/aws
    │ for more information about providing credentials.
    │ 
    │ Error: failed to refresh cached credentials, no EC2 IMDS role found, operation error ec2imds: GetMetadata, request canceled, context deadline exceeded
    │ 
    ╵
    ```

- [X] End up creating .sh script to run the whole thing
- [X] Check if Glue is working in ETL
- [X] Add CloudWatch trigger to ETL
- [X] Create a lambda and API Gateway to provide the data for this workshop
- [ ] Write a code for ETL
- [ ] Check if Athena is working after ETL
- [X] Create a .ps1 script to run the whole thing
- [ ] Make a presentation???
