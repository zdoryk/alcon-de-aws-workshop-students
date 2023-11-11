# Create API Gateway with Rest API type
resource "aws_api_gateway_rest_api" "example" {
  name        = "Alcon data API"
  description = "Will return the data that automatically generates each 5 mins"
}

resource "aws_api_gateway_resource" "data_resource" {
   rest_api_id = aws_api_gateway_rest_api.example.id
   parent_id   = aws_api_gateway_rest_api.example.root_resource_id
   path_part   = "data"
}

# Create a method for GET requests on /data/
resource "aws_api_gateway_method" "get_data" {
   rest_api_id   = aws_api_gateway_rest_api.example.id
   resource_id   = aws_api_gateway_resource.data_resource.id
   http_method   = "GET"
   authorization = "NONE"

   request_parameters = {
     "method.request.querystring.date"       = true
     "method.request.querystring.start_time" = true
     "method.request.querystring.end_time"   = true
     "method.request.header.Authorization"    = true
   }
}

# Configure integration for the GET method
resource "aws_api_gateway_integration" "get_data_integration" {
   rest_api_id = aws_api_gateway_rest_api.example.id
   resource_id = aws_api_gateway_method.get_data.resource_id
   http_method = aws_api_gateway_method.get_data.http_method

   integration_http_method = "POST"
   type                    = "AWS_PROXY"
   uri                     = aws_lambda_function.lambda_function.invoke_arn
}

## Create OPTIONS method to handle pre-flight requests for CORS
#resource "aws_api_gateway_method" "options_method" {
#  rest_api_id = aws_api_gateway_rest_api.example.id
#  resource_id = aws_api_gateway_method.get_data.resource_id
#  http_method = "OPTIONS"
#  authorization = "NONE"
#}

# Configure integration for the OPTIONS method
#resource "aws_api_gateway_integration" "options_integration" {
#  rest_api_id = aws_api_gateway_rest_api.example.id
#  resource_id = aws_api_gateway_method.options_method.resource_id
#  http_method = aws_api_gateway_method.options_method.http_method
#  integration_http_method = "OPTIONS"
#  type = "MOCK"
#  passthrough_behavior = "WHEN_NO_MATCH"
#  request_templates = {
#    "application/json" = "{\"statusCode\": 200}"
#  }
#}

# Configure method response for the OPTIONS method
#resource "aws_api_gateway_method_response" "options_response" {
#  rest_api_id = aws_api_gateway_rest_api.example.id
#  resource_id = aws_api_gateway_method.options_method.resource_id
#  http_method = aws_api_gateway_method.options_method.http_method
#  status_code = "200"
#  response_parameters = {
#    "method.response.header.Access-Control-Allow-Headers" = true
#    "method.response.header.Access-Control-Allow-Methods" = true
#    "method.response.header.Access-Control-Allow-Origin"  = true
#  }
#}
#
## Configure integration response for the OPTIONS method
#resource "aws_api_gateway_integration_response" "options_response" {
#  rest_api_id = aws_api_gateway_rest_api.example.id
#  resource_id = aws_api_gateway_method.options_method.resource_id
#  http_method = aws_api_gateway_method.options_method.http_method
#  status_code = aws_api_gateway_method_response.options_response.status_code
#  response_parameters = {
#    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
#    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
#    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
#  }
#}

# Deploy API Gateway
resource "aws_api_gateway_deployment" "example" {
  depends_on = [
    aws_api_gateway_integration.get_data_integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.example.id
  stage_name  = "v1"
}

# Output to the URL
output "base_url" {
  value = aws_api_gateway_deployment.example.invoke_url
}
