variable "agent_name" {
  description = "Name of the agent (used for ECR repository naming)"
  type        = string
}

variable "ecr_region" {
  description = "AWS region for ECR repository"
  type        = string
  default     = "us-east-1"
}

variable "image_tag_mutability" {
  description = "The tag mutability setting for the repository"
  type        = string
  default     = "MUTABLE"
}

variable "scan_on_push" {
  description = "Indicates whether images are scanned after being pushed to the repository"
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "build_image" {
  description = "Whether to build and push the Docker image"
  type        = bool
  default     = true
}
