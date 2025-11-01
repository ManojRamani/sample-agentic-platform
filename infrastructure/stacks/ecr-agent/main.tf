terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.ecr_region
}

module "ecr_agent" {
  source = "../../modules/ecr-agent"

  agent_name   = var.agent_name
  ecr_region   = var.ecr_region
  common_tags  = var.common_tags
  build_image  = true
}
