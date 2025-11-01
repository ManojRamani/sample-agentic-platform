data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  # Create a runtime name that will always start with a letter when module adds its prefix
  # Module does: ${random_prefix}_${runtime_name}
  # So we make runtime_name start with a letter to ensure the final result is valid
  sanitized_agent_name = "${replace(var.agent_name, "-", "_")}"
}

module "agentcore-memory" {
  source = "../../modules/agentcore-memory"

  # variables
  memory_name = "${local.sanitized_agent_name}_memory"
  expiration_duration = 7
}

module "agentcore" {
  source  = "../../modules/agentcore"

  # Enable Agent Core Runtime
  create_runtime = true
  runtime_name = local.sanitized_agent_name
  runtime_description = var.agent_description
  
  # docker container ECR url passed externally
  runtime_container_uri = var.image_uri_latest
  runtime_network_mode = var.network_mode
  runtime_role_arn = null  # Let module create its own role
  
  # Environment variables for the runtime
  runtime_environment_variables = var.environment_variables
  
  # Required authorizer configuration (empty for no authorization)
  runtime_authorizer_configuration = var.authorizer_configuration
  
  # Enable Agent Core Runtime Endpoint
  create_runtime_endpoint = var.create_endpoint
  runtime_endpoint_name = "${local.sanitized_agent_name}Endpoint"
  runtime_endpoint_description = "Endpoint for ${var.agent_name} runtime" 

}
