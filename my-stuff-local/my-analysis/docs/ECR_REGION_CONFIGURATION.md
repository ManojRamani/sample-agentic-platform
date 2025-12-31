# ECR Region Configuration Guide

This document explains how to configure the ECR (Elastic Container Registry) region for deploying agents in the agentic platform.

## Overview

By default, ECR repositories are created in `us-east-1`, but you can configure this to use any AWS region that supports ECR. This is useful for:

- **Compliance Requirements**: Some organizations require data to stay in specific regions
- **Performance Optimization**: Deploying ECR closer to your compute resources reduces image pull times
- **Cost Optimization**: Some regions have lower ECR storage costs
- **Multi-Region Deployments**: Supporting agents deployed across different regions

## Configuration Methods

### Method 1: Terraform Variables (Recommended)

The most straightforward way is to modify the `ecr_region` parameter in your agent's tfvars file.

#### Step 1: Update the tfvars file
Edit `infrastructure/stacks/ecr-agent/<agent-name>.tfvars`:

```hcl
agent_name = "agentic_chat_enhanced"
ecr_region = "us-west-2"  # Change this to your desired ECR region

common_tags = {
  Project     = "agentic-platform"
  Agent       = "agentic_chat_enhanced"
  Environment = "shared"
  ManagedBy   = "terraform"
}
```

#### Step 2: Deploy with the new region
```bash
./deploy/deploy-agent.sh agentic_chat_enhanced
```

### Method 2: Environment Variable Override

You can also override the region using environment variables during deployment:

```bash
# Set the ECR region
export AWS_REGION=us-west-2

# Deploy the agent
./deploy/deploy-agent.sh agentic_chat_enhanced
```

### Method 3: Direct Terraform Command

For advanced users, you can override the region directly with Terraform:

```bash
cd infrastructure/stacks/ecr-agent
terraform apply -var="ecr_region=us-west-2" -var-file="agentic_chat_enhanced.tfvars" -auto-approve
```

## Supported Regions

ECR is available in most AWS regions. Common choices include:

| Region Code | Region Name | Notes |
|-------------|-------------|-------|
| `us-east-1` | US East (N. Virginia) | Default, lowest cost |
| `us-west-2` | US West (Oregon) | Popular for west coast deployments |
| `eu-west-1` | Europe (Ireland) | GDPR compliance |
| `ap-southeast-1` | Asia Pacific (Singapore) | Asia deployments |
| `ap-northeast-1` | Asia Pacific (Tokyo) | Japan deployments |

For a complete list, see [AWS ECR Regional Availability](https://docs.aws.amazon.com/general/latest/gr/ecr.html).

## Architecture Impact

### Single Region Deployment
```
┌─────────────────────────────────────────────────────────────┐
│                    Single Region (us-west-2)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   ECR Registry  │  │  Agent-Core     │  │     EKS     │  │
│  │   us-west-2     │  │   us-west-2     │  │  us-west-2  │  │
│  │                 │  │                 │  │             │  │
│  │ • Fast pulls    │  │ • Low latency   │  │ • Fast boot │  │
│  │ • Single region │  │ • Same region   │  │ • Optimal   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Region Deployment
```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Region Setup                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   ECR Registry  │  │  Agent-Core     │  │     EKS     │  │
│  │   us-east-1     │  │   us-west-2     │  │  eu-west-1  │  │
│  │                 │  │                 │  │             │  │
│  │ • Central repo  │  │ • Cross-region  │  │ • Global    │  │
│  │ • Single image  │  │ • Image pulls   │  │ • Deployment│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

### 1. Region Selection Criteria

**Performance**: Choose the region closest to your compute resources:
```bash
# If your EKS cluster is in us-west-2, use us-west-2 for ECR
ecr_region = "us-west-2"
```

**Compliance**: Match your data residency requirements:
```bash
# For GDPR compliance in Europe
ecr_region = "eu-west-1"
```

**Cost**: Consider ECR pricing differences:
```bash
# us-east-1 typically has the lowest costs
ecr_region = "us-east-1"
```

### 2. Naming Conventions

Use region-aware naming for multi-region deployments:

```hcl
agent_name = "agentic_chat_enhanced"
ecr_region = "us-west-2"

common_tags = {
  Project     = "agentic-platform"
  Agent       = "agentic_chat_enhanced"
  Environment = "shared"
  Region      = "us-west-2"  # Add region tag
  ManagedBy   = "terraform"
}
```

### 3. Cross-Region Considerations

When ECR and compute resources are in different regions:

```bash
# ECR in us-east-1 (cost optimization)
ecr_region = "us-east-1"

# But EKS cluster in us-west-2
# Image pulls will cross regions (additional latency + data transfer costs)
```

**Recommendation**: Keep ECR and compute in the same region unless you have specific requirements.

### 4. Multi-Agent Deployments

For multiple agents, you can use different regions:

```bash
# Agent 1: Chat agent in us-east-1
infrastructure/stacks/ecr-agent/agentic_chat.tfvars:
ecr_region = "us-east-1"

# Agent 2: RAG agent in us-west-2  
infrastructure/stacks/ecr-agent/agentic_rag.tfvars:
ecr_region = "us-west-2"
```

## Migration Between Regions

### Step 1: Create New ECR Repository
```bash
# Update the region in tfvars
ecr_region = "us-west-2"

# Deploy to create new repository
./deploy/deploy-agent.sh agentic_chat_enhanced
```

### Step 2: Update Runtime Configurations
The deployment script automatically updates:
- Agent-Core runtime configuration
- EKS Helm values
- Container image references

### Step 3: Cleanup Old Repository (Optional)
```bash
# Delete old ECR repository in previous region
aws ecr delete-repository --repository-name agentic-platform-agentic_chat_enhanced --region us-east-1 --force
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```bash
Error: Failed to authenticate with ECR
```

**Solution**: Ensure AWS credentials have ECR permissions in the target region:
```bash
aws ecr get-login-password --region us-west-2
```

#### 2. Repository Not Found
```bash
Error: Repository does not exist
```

**Solution**: The deployment script automatically creates repositories, but ensure the region is correct:
```bash
aws ecr describe-repositories --region us-west-2
```

#### 3. Cross-Region Access Issues
```bash
Error: Image pull failed
```

**Solution**: Verify the image URI includes the correct region:
```bash
# Correct format
423623854297.dkr.ecr.us-west-2.amazonaws.com/agentic-platform-agentic_chat_enhanced:latest
```

### Validation Commands

```bash
# Check ECR repository exists in target region
aws ecr describe-repositories --repository-names agentic-platform-agentic_chat_enhanced --region us-west-2

# List images in repository
aws ecr list-images --repository-name agentic-platform-agentic_chat_enhanced --region us-west-2

# Test image pull
docker pull 423623854297.dkr.ecr.us-west-2.amazonaws.com/agentic-platform-agentic_chat_enhanced:latest
```

## Cost Considerations

### ECR Pricing by Region (as of 2024)

| Region | Storage (per GB/month) | Data Transfer Out |
|--------|----------------------|-------------------|
| us-east-1 | $0.10 | $0.09/GB |
| us-west-2 | $0.10 | $0.09/GB |
| eu-west-1 | $0.10 | $0.09/GB |

### Cross-Region Data Transfer

When ECR and compute are in different regions:
- **Same Region**: No data transfer charges
- **Cross-Region**: $0.02/GB between US regions, $0.09/GB to other regions

### Optimization Tips

1. **Co-locate ECR and Compute**: Keep them in the same region
2. **Use Image Caching**: EKS nodes cache pulled images
3. **Optimize Image Size**: Smaller images = lower transfer costs
4. **Consider Reserved Capacity**: For high-volume deployments

## Example Configurations

### Development Environment
```hcl
# Use us-east-1 for lowest cost
agent_name = "agentic_chat_enhanced"
ecr_region = "us-east-1"

common_tags = {
  Project     = "agentic-platform"
  Agent       = "agentic_chat_enhanced"
  Environment = "development"
  ManagedBy   = "terraform"
}
```

### Production Environment
```hcl
# Use same region as production workloads
agent_name = "agentic_chat_enhanced"
ecr_region = "us-west-2"

common_tags = {
  Project     = "agentic-platform"
  Agent       = "agentic_chat_enhanced"
  Environment = "production"
  ManagedBy   = "terraform"
}
```

### Multi-Region Production
```hcl
# Primary region for ECR
agent_name = "agentic_chat_enhanced"
ecr_region = "us-east-1"

common_tags = {
  Project     = "agentic-platform"
  Agent       = "agentic_chat_enhanced"
  Environment = "production"
  Scope       = "global"
  ManagedBy   = "terraform"
}
```

## Summary

The ECR region configuration provides flexibility for:
- **Performance**: Reduce image pull latency
- **Compliance**: Meet data residency requirements  
- **Cost**: Optimize for storage and transfer costs
- **Scale**: Support multi-region deployments

Simply update the `ecr_region` parameter in your agent's tfvars file and redeploy to change regions. The deployment automation handles all the necessary updates to runtime configurations and image references.
