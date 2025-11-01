data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Configure provider for ECR region
provider "aws" {
  alias  = "ecr"
  region = var.ecr_region
}

resource "aws_ecr_repository" "agent_repo" {
  provider = aws.ecr
  
  name                 = "agentic-platform-${var.agent_name}"
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  tags = merge(var.common_tags, {
    Name = "agentic-platform-${var.agent_name}"
    Type = "ECR Repository"
  })
}

# Build and push Docker image using existing build script
resource "null_resource" "docker_image" {
  count = var.build_image ? 1 : 0
  
  depends_on = [aws_ecr_repository.agent_repo]

  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    working_dir = "../../.."
    command     = "./deploy/build-container.sh ${var.agent_name} agent"
  }
}
