terraform {
  backend "s3" {
    bucket = "agentptfm-bootstrap-terraform-state-02f9f73d0739"
    key    = "agentcore-runtime/terraform.tfstate"
    region = "us-west-2"
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
    awscc = {
      source  = "hashicorp/awscc"
      version = ">= 1.0.0"
    }
  }
}
