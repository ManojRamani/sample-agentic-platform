variable "agent_name" {
  description = "Name of the agent"
  type        = string
}

variable "agent_description" {
  description = "Description of the agent"
  type        = string
  default     = "Custom runtime agent"
}

variable "image_uri_latest" {
  description = "Full ECR URI for the Docker image with latest tag"
  type        = string
}

variable "network_mode" {
  description = "Network mode for the runtime"
  type        = string
  default     = "PUBLIC"
}

variable "environment_variables" {
  description = "Environment variables for the runtime"
  type        = map(string)
  default = {
    "LOG_LEVEL" = "INFO"
    "ENV"       = "production"
  }
}

variable "create_endpoint" {
  description = "Whether to create runtime endpoint"
  type        = bool
  default     = true
}

variable "create_runtime" {
  description = "Whether to create the runtime (set to false initially until image is pushed)"
  type        = bool
  default     = false
}

variable "authorizer_configuration" {
  description = "Authorizer configuration for the runtime"
  type        = any
  default     = null
}

variable "memory_name_suffix" {
  description = "Suffix for memory name to avoid conflicts"
  type        = string
  default     = ""
}
