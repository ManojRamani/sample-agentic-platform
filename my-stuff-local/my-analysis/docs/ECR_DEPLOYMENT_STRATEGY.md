# ECR Deployment Strategy for Agentic Platform

This document outlines the ECR (Elastic Container Registry) deployment strategy that separates Docker image creation from runtime deployment, enabling clean separation of concerns and reusable infrastructure.

## Overview

The ECR deployment strategy implements a three-layer architecture:

1. **ECR Layer**: Creates ECR repositories and builds/pushes Docker images
2. **Agent-Core Runtime Layer**: Deploys agents to AWS Agent Core runtime
3. **EKS Runtime Layer**: Deploys agents to Kubernetes (EKS)

## Architecture Benefits

### Separation of Concerns
- **ECR Management**: Centralized container image lifecycle
- **Runtime Deployment**: Independent deployment to different runtimes
- **Configuration Management**: Environment-specific configurations

### Reusability
- **Single ECR Repository**: One repository serves multiple runtimes
- **Shared ECR Module**: Reusable across multiple agents
- **Consistent Image**: Same Docker image, different runtime configurations

### Cost Efficiency
- **Single Repository**: Reduces storage costs
- **Shared Infrastructure**: Amortized ECR management costs
- **Optimized Builds**: Single build process for multiple deployments

## Implementation Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ECR Stack     │    │ Agent-Core Stack │    │   EKS Stack     │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ ECR Module  │ │───▶│ │ AgentCore    │ │    │ │ Helm Chart  │ │
│ │             │ │    │ │ Module       │ │    │ │             │ │
│ │ - Repository│ │    │ │              │ │    │ │ - K8s Deploy│ │
│ │ - Build     │ │    │ │ - Runtime    │ │    │ │ - Service   │ │
│ │ - Push      │ │    │ │ - Endpoint   │ │    │ │ - Ingress   │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ ECR Repository  │    │ Agent Core       │    │ EKS Cluster     │
│                 │    │ Runtime          │    │                 │
│ agentic-        │    │                  │    │ Pod: agent      │
│ platform-       │    │ Lambda/Container │    │ Service: agent  │
│ agent_name      │    │                  │    │ Ingress: /agent │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Directory Structure

```
├── src/agentic_platform/agent/agentic_chat_enhanced/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── server.py
│   └── [agent code]
├── infrastructure/
│   ├── modules/ecr-agent/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   └── stacks/
│       ├── ecr-agent/
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   ├── outputs.tf
│       │   └── agentic_chat_enhanced.tfvars
│       └── agentcore-runtime/
│           └── agentic_chat_enhanced.tfvars
├── k8s/helm/values/applications/
│   └── agentic-chat-enhanced-values.yaml
├── deploy/
│   └── deploy-agent.sh
└── docs/
    └── ECR_DEPLOYMENT_STRATEGY.md
```

## Component Details

### 1. ECR Module (`infrastructure/modules/ecr-agent/`)

**Purpose**: Reusable Terraform module for ECR repository management

**Features**:
- Creates ECR repository with configurable settings
- Builds and pushes Docker images using existing build script
- Supports image vulnerability scanning
- Provides comprehensive outputs for integration

**Key Files**:
- `main.tf`: ECR repository and build resources
- `variables.tf`: Input parameters
- `outputs.tf`: Repository URLs and metadata
- `README.md`: Module documentation

### 2. ECR Stack (`infrastructure/stacks/ecr-agent/`)

**Purpose**: Terraform stack that uses the ECR module to create repositories

**Features**:
- Agent-specific ECR repository creation
- Docker image building and pushing
- Output ECR URIs for runtime consumption

**Key Files**:
- `main.tf`: Stack configuration using ECR module
- `agentic_chat_enhanced.tfvars`: Agent-specific variables

### 3. Agent-Core Runtime Configuration

**Purpose**: Configuration for deploying to AWS Agent Core runtime

**Features**:
- Consumes ECR image URI from ECR stack
- Environment-specific configuration
- CloudFront endpoint integration

**Key Files**:
- `agentic_chat_enhanced.tfvars`: Runtime configuration

### 4. EKS Configuration

**Purpose**: Helm values for Kubernetes deployment

**Features**:
- Consumes ECR repository URL
- Kubernetes-native service endpoints
- IRSA integration for AWS permissions

**Key Files**:
- `agentic-chat-enhanced-values.yaml`: Helm values

### 5. Deployment Automation

**Purpose**: Automated deployment script for end-to-end deployment

**Features**:
- Sequential deployment (ECR → Agent-Core → EKS)
- Automatic configuration updates
- Error handling and rollback

**Key Files**:
- `deploy-agent.sh`: Deployment automation script

## Deployment Workflow

### Manual Deployment

```bash
# 1. Deploy ECR stack
cd infrastructure/stacks/ecr-agent
terraform init
terraform apply -var-file="agentic_chat_enhanced.tfvars"

# Get ECR outputs
ECR_IMAGE_URI=$(terraform output -raw image_uri_latest)
ECR_REPOSITORY=$(terraform output -raw repository_url)

# 2. Update Agent-Core runtime configuration
cd ../agentcore-runtime
sed -i "s|PLACEHOLDER_ECR_URI|$ECR_IMAGE_URI|g" agentic_chat_enhanced.tfvars
terraform apply -var-file="agentic_chat_enhanced.tfvars"

# 3. Update EKS configuration
cd ../../k8s
sed -i "s|PLACEHOLDER_ECR_REPOSITORY|$ECR_REPOSITORY|g" helm/values/applications/agentic-chat-enhanced-values.yaml
helm upgrade --install agentic-chat-enhanced ./helm/charts/agentic-service \
  -f ./helm/values/applications/agentic-chat-enhanced-values.yaml
```

### Automated Deployment

```bash
# Single command deployment
./deploy/deploy-agent.sh agentic_chat_enhanced
```

## Configuration Patterns

### Environment Variables

**Agent-Core Runtime** (External endpoints):
```hcl
environment_variables = {
  "ENVIRONMENT": "local",
  "LITELLM_API_ENDPOINT": "https://d39czc0wfea9rq.cloudfront.net/frontend/api/litellm",
  "LITELLM_KEY": "sk-..."
}
```

**EKS Runtime** (Internal service endpoints):
```yaml
configDefaults:
  LITELLM_API_ENDPOINT: "http://litellm.default.svc.cluster.local:80"
  RETRIEVAL_GATEWAY_ENDPOINT: "http://retrieval-gateway.default.svc.cluster.local:80/api/retrieval-gateway"
  MEMORY_GATEWAY_ENDPOINT: "http://memory-gateway.default.svc.cluster.local:80/api/memory-gateway"
```

### Naming Conventions

| Component | Pattern | Example |
|-----------|---------|---------|
| Agent Directory | `agentic_chat_enhanced` | `src/agentic_platform/agent/agentic_chat_enhanced/` |
| ECR Repository | `agentic-platform-{agent_name}` | `agentic-platform-agentic_chat_enhanced` |
| K8s Service | `{agent_name}` (hyphens) | `agentic-chat-enhanced` |
| Terraform Files | `{agent_name}.tfvars` | `agentic_chat_enhanced.tfvars` |
| Helm Values | `{agent_name}-values.yaml` | `agentic-chat-enhanced-values.yaml` |

## Security Considerations

### ECR Security
- Image vulnerability scanning enabled by default
- Repository access controlled via IAM policies
- Multi-architecture image support (AMD64/ARM64)

### Runtime Security
- **Agent-Core**: IAM roles and policies for AWS service access
- **EKS**: IRSA (IAM Roles for Service Accounts) integration
- **Secrets**: AWS Secrets Manager integration

### Network Security
- **Agent-Core**: CloudFront distribution for external access
- **EKS**: Internal service mesh communication
- **Container**: Non-root user execution

## Monitoring and Observability

### ECR Monitoring
- CloudWatch metrics for repository usage
- Image scan results and vulnerability reports
- Build success/failure tracking

### Runtime Monitoring
- **Agent-Core**: CloudWatch logs and metrics
- **EKS**: Kubernetes native monitoring
- **Application**: Health check endpoints

## Troubleshooting

### Common Issues

1. **ECR Authentication Failures**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   ```

2. **Build Script Failures**
   - Verify Docker is running
   - Check AWS credentials
   - Ensure agent Dockerfile exists

3. **Terraform State Issues**
   ```bash
   terraform refresh
   terraform plan
   ```

4. **Helm Deployment Issues**
   ```bash
   helm list
   helm status agentic-chat-enhanced
   kubectl logs -l app=agentic-chat-enhanced
   ```

### Validation Commands

```bash
# Verify ECR repository
aws ecr describe-repositories --repository-names agentic-platform-agentic_chat_enhanced

# Verify image exists
aws ecr list-images --repository-name agentic-platform-agentic_chat_enhanced

# Verify EKS deployment
kubectl get pods -l app=agentic-chat-enhanced
kubectl get services agentic-chat-enhanced
```

## Best Practices

### Development Workflow
1. Develop agent code locally
2. Test with docker-compose
3. Deploy ECR stack for image building
4. Deploy to staging runtime first
5. Deploy to production runtime

### Version Management
- Use semantic versioning for image tags
- Tag images for different environments
- Maintain separate configurations per environment

### Cost Optimization
- Use lifecycle policies for old images
- Monitor repository storage usage
- Optimize Docker image layers

## Future Enhancements

### Planned Features
- Multi-environment support (dev/staging/prod)
- Automated CI/CD pipeline integration
- Blue-green deployment support
- Cross-region ECR replication

### Scalability Considerations
- ECR repository per agent pattern scales horizontally
- Shared ECR module reduces infrastructure duplication
- Runtime-agnostic deployment enables multi-cloud strategies

## Conclusion

This ECR deployment strategy provides a robust, scalable, and maintainable approach to deploying agentic platform agents across multiple runtimes. The separation of concerns between image creation and runtime deployment enables teams to:

- Develop and deploy independently
- Reuse infrastructure components
- Maintain consistent deployment patterns
- Scale efficiently across multiple agents and environments

The strategy has been successfully implemented with the `agentic_chat_enhanced` agent and can be replicated for additional agents following the same patterns and conventions.
