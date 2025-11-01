# Platform AgentCore Stack

> **📋 Prerequisites for Viewing Diagrams**
> 
> This README contains Mermaid diagrams for visualizing the architecture and workflows. To view these diagrams properly, please install a Mermaid plugin/extension for your editor or browser:
> 
> - **VS Code**: Install the "Markdown Preview Mermaid Support" extension
> - **GitHub**: Mermaid diagrams are natively supported in GitHub markdown
> - **Browser**: Use the "Mermaid Diagrams" browser extension or view on GitHub
> - **Alternative**: Copy the mermaid code to [mermaid.live](https://mermaid.live) for online rendering

This Terraform stack deploys a "lite" version of the agentic platform using ECS instead of EKS. It provides a complete platform infrastructure for running AI agents with LiteLLM as the model proxy service.

## Overview

The Platform AgentCore stack creates a containerized platform that includes:

- **ECS Cluster**: Fargate-based container orchestration for LiteLLM
- **LiteLLM Service**: AI model proxy for accessing multiple LLM providers
- **PostgreSQL Aurora**: Database for application data and LiteLLM configuration
- **Redis ElastiCache**: Caching layer for improved performance
- **Cognito Authentication**: User authentication and authorization
- **CloudFront + S3**: Static website hosting for frontend applications
- **Bastion Host**: Secure access to VPC resources
- **Parameter Store**: Centralized configuration management

## Prerequisites

Before deploying the Platform AgentCore stack, ensure you have:

### 1. Foundation Infrastructure
- **Foundation Stack**: Must be deployed first (`infrastructure/stacks/foundation/`)
- **VPC and Networking**: VPC, subnets, and security groups from foundation
- **KMS Keys**: Optional encryption keys from foundation stack

### 2. Required Tools
- **Terraform**: Version >= 1.0
- **AWS CLI**: Configured with appropriate permissions
- **Docker**: For local testing (optional)

### 3. AWS Permissions
Your AWS credentials must have permissions for:
- ECS cluster and service management
- ECR repository operations (if using custom images)
- RDS Aurora cluster management
- ElastiCache cluster management
- Cognito user pool operations
- S3 bucket and CloudFront distribution management
- IAM role and policy management
- Secrets Manager operations
- Parameter Store operations

### 4. Foundation Stack Outputs
You'll need the following outputs from your foundation stack:
- VPC ID and CIDR block
- Private and public subnet IDs
- KMS key ARN and ID (if encryption is enabled)

## Architecture Overview

```mermaid
graph TB
    subgraph "Internet"
        USER[Users/Clients]
        LLMPROV[LLM Providers<br/>OpenAI, Anthropic, etc.]
    end

    subgraph "AWS Account"
        subgraph "CloudFront + S3"
            CF[CloudFront Distribution]
            S3[S3 Static Website<br/>Frontend Apps]
        end

        subgraph "Application Load Balancer"
            ALB[ALB<br/>LiteLLM Gateway]
        end

        subgraph "ECS Cluster"
            subgraph "Fargate Tasks"
                LITELLM[LiteLLM Service<br/>AI Model Proxy]
            end
        end

        subgraph "Data Layer"
            POSTGRES[(PostgreSQL Aurora<br/>Application Data)]
            REDIS[(Redis ElastiCache<br/>Caching Layer)]
        end

        subgraph "Security & Access"
            COGNITO[Cognito<br/>Authentication]
            BASTION[Bastion Host<br/>VPC Access]
            SECRETS[Secrets Manager<br/>API Keys & Credentials]
        end

        subgraph "Configuration"
            PARAMS[Parameter Store<br/>Platform Config]
        end
    end

    %% User flows
    USER --> CF
    CF --> S3
    CF --> ALB
    ALB --> LITELLM

    %% LiteLLM connections
    LITELLM --> POSTGRES
    LITELLM --> REDIS
    LITELLM --> SECRETS
    LITELLM --> LLMPROV

    %% Authentication flow
    USER --> COGNITO
    COGNITO --> LITELLM

    %% Management access
    BASTION --> POSTGRES
    BASTION --> REDIS
    BASTION --> SECRETS

    %% Configuration
    LITELLM --> PARAMS

    %% Styling
    classDef user fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef aws fill:#ff9900,stroke:#232f3e,stroke-width:2px,color:#fff
    classDef compute fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    classDef data fill:#51cf66,stroke:#2b8a3e,stroke-width:2px,color:#fff
    classDef security fill:#ffd43b,stroke:#fab005,stroke-width:2px,color:#000
    classDef external fill:#868e96,stroke:#495057,stroke-width:2px,color:#fff

    class USER,LLMPROV external
    class CF,S3,ALB aws
    class LITELLM compute
    class POSTGRES,REDIS data
    class COGNITO,BASTION,SECRETS,PARAMS security
```

## Component Dependencies

```mermaid
graph TD
    subgraph "Foundation Stack (Required)"
        VPC[VPC & Networking]
        KMS[KMS Keys<br/>Optional]
    end

    subgraph "Platform AgentCore Components"
        POSTGRES[PostgreSQL Aurora]
        REDIS[Redis ElastiCache]
        COGNITO[Cognito Auth]
        LITELLM_SECRETS[LiteLLM Secrets]
        ECS[ECS LiteLLM Service]
        BASTION[Bastion Host]
        S3_WEB[S3 Website]
        CLOUDFRONT[CloudFront]
        PARAMS[Parameter Store]
    end

    %% Dependencies
    VPC --> POSTGRES
    VPC --> REDIS
    VPC --> ECS
    VPC --> BASTION
    
    KMS --> POSTGRES
    KMS --> REDIS
    KMS --> LITELLM_SECRETS
    
    POSTGRES --> LITELLM_SECRETS
    REDIS --> LITELLM_SECRETS
    LITELLM_SECRETS --> ECS
    
    POSTGRES --> ECS
    REDIS --> ECS
    POSTGRES --> BASTION
    REDIS --> BASTION
    
    S3_WEB --> CLOUDFRONT
    ECS --> CLOUDFRONT
    
    %% Parameter Store depends on all components
    POSTGRES --> PARAMS
    REDIS --> PARAMS
    COGNITO --> PARAMS
    ECS --> PARAMS
    S3_WEB --> PARAMS
    CLOUDFRONT --> PARAMS

    %% Styling
    classDef foundation fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000

    class VPC,KMS foundation
    class POSTGRES,REDIS,COGNITO,LITELLM_SECRETS,ECS,BASTION,S3_WEB,CLOUDFRONT,PARAMS component
```

## Step-by-Step Deployment Guide

### Step 1: Verify Foundation Stack

Ensure your foundation stack is deployed and gather required outputs:

```bash
# Navigate to foundation stack
cd infrastructure/stacks/foundation

# Get foundation outputs
terraform output vpc_id
terraform output vpc_cidr_block
terraform output private_subnet_ids
terraform output public_subnet_ids

# If KMS is enabled
terraform output kms_key_arn
terraform output kms_key_id
```

### Step 2: Navigate to Platform AgentCore Directory

```bash
cd infrastructure/stacks/platform-agentcore
```

### Step 3: Create Configuration File

Copy and customize the configuration file:

```bash
# Copy the example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit the configuration
vim terraform.tfvars
```

**Example Configuration** (`terraform.tfvars`):
```hcl
########################################################
# Core Configuration
########################################################

aws_region   = "us-west-2"
environment  = "dev"
name_prefix  = "agentcore-"

########################################################
# Networking Configuration (from foundation stack)
########################################################

vpc_id         = "vpc-0123456789abcdef0"
vpc_cidr_block = "10.0.0.0/16"

private_subnet_ids = [
  "subnet-0123456789abcdef0",
  "subnet-0123456789abcdef1"
]

public_subnet_ids = [
  "subnet-0123456789abcdef2",
  "subnet-0123456789abcdef3"
]

########################################################
# KMS Configuration (optional)
########################################################

enable_kms_encryption = false
kms_key_arn = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
kms_key_id  = "12345678-1234-1234-1234-123456789012"

########################################################
# PostgreSQL Configuration
########################################################

postgres_instance_count       = 1
postgres_instance_class      = "db.serverless"
postgres_deletion_protection = false
postgres_iam_username        = "postgres_iam_user"

########################################################
# Redis Configuration
########################################################

redis_node_type                 = "cache.t3.micro"
redis_engine_version           = "7.0"
redis_num_cache_clusters       = 2  # Minimum 2 required for automatic failover
redis_maintenance_window       = "sun:05:00-sun:06:00"
redis_snapshot_window          = "03:00-04:00"
redis_snapshot_retention_limit = 1

########################################################
# ECS LiteLLM Configuration
########################################################

litellm_cpu                  = 1024  # 1 vCPU
litellm_memory              = 2048   # 2 GB
litellm_desired_count       = 1
litellm_enable_auto_scaling = true
litellm_min_capacity        = 1
litellm_max_capacity        = 3

########################################################
# S3 Configuration
########################################################

s3_force_destroy = true  # Set to false for production
```

### Step 4: Initialize Terraform

```bash
terraform init
```

### Step 5: Plan the Deployment

```bash
terraform plan
```

Review the plan to ensure all resources will be created correctly.

### Step 6: Deploy the Platform

```bash
terraform apply
```

**What happens during deployment:**

1. **PostgreSQL Aurora Cluster** is created with security groups
2. **Redis ElastiCache** cluster is provisioned
3. **Cognito User Pool** and clients are configured
4. **LiteLLM Secrets** are created in Secrets Manager
5. **ECS Cluster** is created with Fargate capacity
6. **ECS Service** deploys LiteLLM containers
7. **Application Load Balancer** is configured for LiteLLM
8. **Bastion Host** is launched for VPC access
9. **S3 Bucket** is created for static website hosting
10. **CloudFront Distribution** is configured
11. **Parameter Store** configuration is populated

### Step 7: Verify Deployment

```bash
# Check all outputs
terraform output

# Verify ECS service is running
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw litellm_service_name)

# Test LiteLLM endpoint
curl -I $(terraform output -raw litellm_load_balancer_url)/health

# Check CloudFront distribution
aws cloudfront get-distribution \
  --id $(terraform output -raw cloudfront_distribution_id)
```

### Step 8: Configure LiteLLM API Keys

After deployment, you need to configure LiteLLM with your AI provider API keys:

```bash
# Get the LiteLLM secret name
SECRET_NAME=$(terraform output -raw litellm_secret_name)

# Update the secret with your API keys
aws secretsmanager update-secret \
  --secret-id $SECRET_NAME \
  --secret-string '{
    "OPENAI_API_KEY": "your-openai-api-key",
    "ANTHROPIC_API_KEY": "your-anthropic-api-key",
    "LITELLM_MASTER_KEY": "your-master-key-for-litellm"
  }'

# Restart ECS service to pick up new secrets
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw litellm_service_name) \
  --force-new-deployment
```

### Step 9: Test the Platform

```bash
# Get platform endpoints
LITELLM_URL=$(terraform output -raw litellm_load_balancer_url)
WEBSITE_URL=$(terraform output -raw spa_website_url)

# Test LiteLLM health
curl $LITELLM_URL/health

# Test LiteLLM models endpoint
curl -H "Authorization: Bearer your-master-key" \
  $LITELLM_URL/v1/models

echo "Platform deployed successfully!"
echo "LiteLLM URL: $LITELLM_URL"
echo "Website URL: $WEBSITE_URL"
```

## Deployment Sequence Diagram

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant TF as Terraform
    participant AWS as AWS Services
    participant Aurora as PostgreSQL Aurora
    participant Redis as ElastiCache Redis
    participant Cognito as Cognito
    participant Secrets as Secrets Manager
    participant ECS as ECS Service
    participant ALB as Load Balancer
    participant S3 as S3 Bucket
    participant CF as CloudFront

    Dev->>TF: terraform apply
    
    Note over TF,AWS: Phase 1: Data Layer
    TF->>Aurora: Create PostgreSQL cluster
    Aurora-->>TF: Cluster ready
    TF->>Redis: Create Redis cluster
    Redis-->>TF: Cluster ready
    
    Note over TF,AWS: Phase 2: Authentication
    TF->>Cognito: Create user pool & clients
    Cognito-->>TF: Auth configured
    
    Note over TF,AWS: Phase 3: Secrets & Configuration
    TF->>Secrets: Create LiteLLM secrets
    Secrets-->>TF: Secrets created
    
    Note over TF,AWS: Phase 4: Compute Layer
    TF->>ECS: Create ECS cluster
    ECS-->>TF: Cluster ready
    TF->>ALB: Create load balancer
    ALB-->>TF: ALB ready
    TF->>ECS: Deploy LiteLLM service
    ECS->>Aurora: Connect to database
    ECS->>Redis: Connect to cache
    ECS->>Secrets: Retrieve API keys
    ECS-->>TF: Service running
    
    Note over TF,AWS: Phase 5: Frontend Infrastructure
    TF->>S3: Create website bucket
    S3-->>TF: Bucket ready
    TF->>CF: Create CloudFront distribution
    CF->>S3: Configure origin
    CF->>ALB: Configure API origin
    CF-->>TF: Distribution ready
    
    TF-->>Dev: Deployment complete
    
    Note over Dev: Manual Step: Configure API Keys
    Dev->>Secrets: Update LiteLLM secrets
    Dev->>ECS: Restart service
    ECS->>Secrets: Load new secrets
```

## Platform Configuration Management

The platform uses AWS Parameter Store to centralize configuration:

```mermaid
graph TB
    subgraph "Parameter Store Configuration"
        PARAM["/agentic-platform/config/agentcore-{env}"]
    end

    subgraph "Configuration Sections"
        INFRA[Infrastructure<br/>VPC, Region, Account]
        ECS_CONFIG[ECS LiteLLM<br/>Service URLs, ARNs]
        COGNITO_CONFIG[Cognito<br/>User Pool, Clients]
        POSTGRES_CONFIG[PostgreSQL<br/>Endpoints, Credentials]
        REDIS_CONFIG[Redis<br/>Endpoints, Auth]
        LITELLM_CONFIG[LiteLLM<br/>Secret ARNs]
        BASTION_CONFIG[Bastion<br/>Instance Details]
        S3_CONFIG[S3<br/>Bucket Names, ARNs]
        CF_CONFIG[CloudFront<br/>Distribution Details]
    end

    PARAM --> INFRA
    PARAM --> ECS_CONFIG
    PARAM --> COGNITO_CONFIG
    PARAM --> POSTGRES_CONFIG
    PARAM --> REDIS_CONFIG
    PARAM --> LITELLM_CONFIG
    PARAM --> BASTION_CONFIG
    PARAM --> S3_CONFIG
    PARAM --> CF_CONFIG

    %% Styling
    classDef param fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef config fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#000

    class PARAM param
    class INFRA,ECS_CONFIG,COGNITO_CONFIG,POSTGRES_CONFIG,REDIS_CONFIG,LITELLM_CONFIG,BASTION_CONFIG,S3_CONFIG,CF_CONFIG config
```

## Accessing Platform Resources

### Via Bastion Host

```bash
# Get bastion instance ID
BASTION_ID=$(terraform output -raw bastion_instance_id)

# Connect to bastion
aws ssm start-session --target $BASTION_ID

# From bastion, access PostgreSQL
psql -h $(terraform output -raw postgres_cluster_endpoint) -U postgres_iam_user -d postgres

# From bastion, access Redis
redis-cli -h $(terraform output -raw redis_primary_endpoint)
```

### Via Parameter Store

```bash
# Get complete platform configuration
aws ssm get-parameter \
  --name $(terraform output -raw parameter_store_name) \
  --with-decryption \
  --query 'Parameter.Value' \
  --output text | jq .
```

## Monitoring and Troubleshooting

### Common Deployment Issues

#### 1. Redis ElastiCache Configuration Error

**Error Message:**
```
Error: "num_cache_clusters": must be at least 2 if automatic_failover_enabled is true
```

**Cause:** The Redis ElastiCache module has automatic failover enabled, which requires at least 2 cache clusters for high availability.

**Solution:**
```bash
# Update your terraform.tfvars file
redis_num_cache_clusters = 2  # Change from 1 to 2
```

**Why this happens:** The ElastiCache module is configured with `automatic_failover_enabled = true` for production reliability, but this requires a minimum of 2 cache clusters to provide failover capability.

#### 2. Foundation Stack Dependencies

**Error Message:**
```
Error: Invalid value for variable "vpc_id": VPC not found
```

**Cause:** The foundation stack hasn't been deployed or the VPC ID is incorrect.

**Solution:**
```bash
# Verify foundation stack is deployed
cd infrastructure/stacks/foundation
terraform output

# Copy the correct values to platform-agentcore terraform.tfvars
cd ../platform-agentcore
vim terraform.tfvars
```

#### 3. ECS Service Startup Issues

**Symptoms:** ECS tasks keep restarting or failing health checks

**Diagnosis:**
```bash
# Check ECS service events
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw litellm_service_name) \
  --query 'services[0].events[0:5]'

# Check task definition
aws ecs describe-task-definition \
  --task-definition $(aws ecs describe-services \
    --cluster $(terraform output -raw ecs_cluster_name) \
    --services $(terraform output -raw litellm_service_name) \
    --query 'services[0].taskDefinition' --output text)
```

**Common Solutions:**
- **Missing API Keys:** Update LiteLLM secrets in Secrets Manager
- **Insufficient Resources:** Increase CPU/memory in terraform.tfvars
- **Network Issues:** Check security groups and subnet routing

#### 4. Database Connection Issues

**Symptoms:** LiteLLM can't connect to PostgreSQL or Redis

**Diagnosis:**
```bash
# Test from bastion host
BASTION_ID=$(terraform output -raw bastion_instance_id)
aws ssm start-session --target $BASTION_ID

# Test PostgreSQL connection
psql -h $(terraform output -raw postgres_cluster_endpoint) -U postgres_iam_user -d postgres

# Test Redis connection
redis-cli -h $(terraform output -raw redis_primary_endpoint) -p 6379 ping
```

**Common Solutions:**
- **Security Groups:** Ensure ECS security group can reach database security groups
- **Subnet Routing:** Verify private subnets have routes to NAT Gateway
- **IAM Permissions:** Check ECS task role has database access permissions

### Health Monitoring

#### ECS Service Health

```bash
# Check ECS service status
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw litellm_service_name)

# View ECS task logs
aws logs tail /ecs/litellm --follow

# Check running tasks
aws ecs list-tasks \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service-name $(terraform output -raw litellm_service_name)
```

#### Load Balancer Health

```bash
# Check ALB target health
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups \
    --load-balancer-arn $(aws elbv2 describe-load-balancers \
      --names $(terraform output -raw ecs_cluster_name)-litellm \
      --query 'LoadBalancers[0].LoadBalancerArn' --output text) \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

# Test LiteLLM health endpoint
curl -I $(terraform output -raw litellm_load_balancer_url)/health
```

#### Database Connectivity

```bash
# Test PostgreSQL connection
aws rds describe-db-clusters \
  --db-cluster-identifier $(terraform output -raw postgres_cluster_id)

# Test Redis connection
aws elasticache describe-replication-groups \
  --replication-group-id $(terraform output -raw redis_cluster_arn | cut -d: -f6)

# Check database security groups
aws ec2 describe-security-groups \
  --group-ids $(terraform output -raw postgres_security_group_id)
```

### Performance Monitoring

#### CloudWatch Metrics

```bash
# ECS CPU and Memory utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=$(terraform output -raw litellm_service_name) \
              Name=ClusterName,Value=$(terraform output -raw ecs_cluster_name) \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# ALB request count and response time
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCount \
  --dimensions Name=LoadBalancer,Value=$(terraform output -raw litellm_load_balancer_arn | cut -d/ -f2-) \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Log Analysis

#### Centralized Logging

```bash
# View LiteLLM application logs
aws logs describe-log-groups --log-group-name-prefix /ecs/litellm

# Stream real-time logs
aws logs tail /ecs/litellm --follow --since 1h

# Search for errors in logs
aws logs filter-log-events \
  --log-group-name /ecs/litellm \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### Common Log Patterns

- **Startup Issues:** Look for database connection errors or missing environment variables
- **API Errors:** Check for authentication failures or rate limiting
- **Performance Issues:** Monitor response times and resource utilization

### Disaster Recovery

#### Backup Verification

```bash
# Check PostgreSQL automated backups
aws rds describe-db-cluster-snapshots \
  --db-cluster-identifier $(terraform output -raw postgres_cluster_id) \
  --snapshot-type automated

# Check Redis backup status
aws elasticache describe-snapshots \
  --replication-group-id $(terraform output -raw redis_cluster_arn | cut -d: -f6)
```

#### Recovery Procedures

1. **Database Recovery:**
   ```bash
   # Restore from automated backup
   aws rds restore-db-cluster-from-snapshot \
     --db-cluster-identifier restored-cluster \
     --snapshot-identifier <snapshot-id>
   ```

2. **ECS Service Recovery:**
   ```bash
   # Force new deployment
   aws ecs update-service \
     --cluster $(terraform output -raw ecs_cluster_name) \
     --service $(terraform output -raw litellm_service_name) \
     --force-new-deployment
   ```

## Updating the Platform

To update the platform configuration:

```bash
# Update terraform.tfvars with new values
vim terraform.tfvars

# Plan the changes
terraform plan

# Apply the changes
terraform apply
```

**Note**: Some changes may require ECS service restarts or database maintenance windows.

## Cleanup

To remove the platform:

```bash
# Destroy all resources
terraform destroy

# Confirm destruction
# Type 'yes' when prompted
```

**Warning**: This will permanently delete all data in PostgreSQL and Redis clusters.

## Configuration Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aws_region` | AWS region for deployment | `us-west-2` | No |
| `environment` | Environment name | `dev` | No |
| `name_prefix` | Prefix for resource names | - | Yes |
| `vpc_id` | VPC ID from foundation stack | - | Yes |
| `vpc_cidr_block` | VPC CIDR block | - | Yes |
| `private_subnet_ids` | Private subnet IDs | - | Yes |
| `public_subnet_ids` | Public subnet IDs | - | Yes |
| `enable_kms_encryption` | Enable KMS encryption | `false` | No |
| `postgres_instance_class` | PostgreSQL instance class | `db.serverless` | No |
| `redis_node_type` | Redis node type | `cache.t3.micro` | No |
| `litellm_cpu` | LiteLLM CPU units | `1024` | No |
| `litellm_memory` | LiteLLM memory (MB) | `2048` | No |

## Outputs

| Output | Description |
|--------|-------------|
| `litellm_load_balancer_url` | LiteLLM service URL |
| `spa_website_url` | Frontend website URL |
| `postgres_cluster_endpoint` | PostgreSQL endpoint |
| `redis_primary_endpoint` | Redis endpoint |
| `cognito_user_pool_id` | Cognito User Pool ID |
| `parameter_store_name` | Configuration parameter name |

## Next Steps

After deploying the Platform AgentCore stack:

1. **Configure LiteLLM API Keys**: Add your AI provider API keys to Secrets Manager
2. **Deploy Frontend Applications**: Upload your frontend apps to the S3 bucket
3. **Deploy Individual Agents**: Use the `agentcore-runtime` stack to deploy specific agents
4. **Set Up Monitoring**: Configure CloudWatch alarms and dashboards
5. **Configure Authentication**: Set up Cognito users and groups as needed

## Related Documentation

- [AgentCore Runtime Deployment](../agentcore-runtime/README-v2.md)
- [Foundation Stack](../foundation/README.md)
- [LiteLLM Documentation](https://docs.litellm.ai/)
