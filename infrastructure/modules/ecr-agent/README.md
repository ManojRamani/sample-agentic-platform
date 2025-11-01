# ECR Agent Module

This Terraform module creates and manages Amazon Elastic Container Registry (ECR) repositories for agentic platform agents. It provides a reusable way to create ECR repositories, build Docker images, and push them to the registry.

## Features

- Creates ECR repository with configurable settings
- Builds and pushes Docker images using the existing build script
- Supports image vulnerability scanning
- Configurable image tag mutability
- Comprehensive outputs for integration with other modules

## Usage

```hcl
module "ecr_agent" {
  source = "../../modules/ecr-agent"

  agent_name   = "agentic_chat_enhanced"
  common_tags  = {
    Project     = "agentic-platform"
    Agent       = "agentic_chat_enhanced"
    Environment = "shared"
    ManagedBy   = "terraform"
  }
  build_image  = true
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| agent_name | Name of the agent (used for ECR repository naming) | `string` | n/a | yes |
| image_tag_mutability | The tag mutability setting for the repository | `string` | `"MUTABLE"` | no |
| scan_on_push | Indicates whether images are scanned after being pushed to the repository | `bool` | `true` | no |
| common_tags | Common tags to apply to all resources | `map(string)` | `{}` | no |
| build_image | Whether to build and push the Docker image | `bool` | `true` | no |

## Outputs

| Name | Description |
|------|-------------|
| repository_url | The URL of the repository |
| repository_name | The name of the repository |
| repository_arn | Full ARN of the repository |
| registry_id | The registry ID where the repository was created |
| image_uri_latest | The URI of the image with latest tag |

## Repository Naming Convention

The module creates ECR repositories with the naming pattern: `agentic-platform-{agent_name}`

For example:
- Agent name: `agentic_chat_enhanced`
- ECR repository: `agentic-platform-agentic_chat_enhanced`

## Docker Image Building

The module uses the existing `deploy/build-container.sh` script to build and push Docker images. The script:

1. Authenticates with ECR
2. Creates the repository if it doesn't exist
3. Builds the Docker image using the agent's Dockerfile
4. Pushes the image with the `latest` tag

## Integration with Runtime Deployments

This module is designed to be used with runtime deployment stacks:

1. **ECR Stack**: Uses this module to create repository and build image
2. **Agent-Core Runtime**: Consumes the ECR image URI for deployment
3. **EKS Runtime**: Consumes the ECR repository URL for Kubernetes deployment

## Example Integration

```hcl
# ECR Stack
module "ecr_agent" {
  source = "../../modules/ecr-agent"
  agent_name = "agentic_chat_enhanced"
}

# Agent-Core Runtime Stack
module "agentcore" {
  source = "../../modules/agentcore"
  runtime_container_uri = module.ecr_agent.image_uri_latest
}
```

## Security Considerations

- Image scanning is enabled by default
- Repository uses mutable tags for development flexibility
- Build script handles ECR authentication securely
- Images are built with multi-architecture support (linux/amd64, linux/arm64)

## Requirements

- AWS CLI configured with appropriate permissions
- Docker installed and running
- Terraform >= 1.0
- Agent source code with Dockerfile in `src/agentic_platform/agent/{agent_name}/`

## Permissions Required

The executing role needs the following permissions:
- `ecr:CreateRepository`
- `ecr:DescribeRepositories`
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:GetDownloadUrlForLayer`
- `ecr:BatchGetImage`
- `ecr:InitiateLayerUpload`
- `ecr:UploadLayerPart`
- `ecr:CompleteLayerUpload`
- `ecr:PutImage`
