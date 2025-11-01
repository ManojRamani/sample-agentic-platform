variable "agent_name" {
  description = "Name of the agent"
  type        = string
}

variable "ecr_region" {
  description = "AWS region for ECR repository"
  type        = string
  default     = "us-east-1"
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
