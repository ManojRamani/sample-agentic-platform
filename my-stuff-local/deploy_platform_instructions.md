# AgentPath Framework: Agent Deployment Instructions

This guide provides step-by-step instructions for deploying an agent in the AgentPath framework, specifically focusing on the `agentic_chat` agent deployment process.

## Overview

The AgentPath framework follows a layered architecture with specific dependencies that must be deployed in order:

1. **Infrastructure Layer**: AWS resources (VPC, EKS, databases, etc.)
2. **Platform Services**: LiteLLM gateway, Memory gateway, Retrieval gateway  
3. **Agent Applications**: Individual agents like `agentic_chat`

## Prerequisites

### Required Tools

Before starting the deployment, ensure you have the following tools installed:

- **[Terraform using tfenv](https://github.com/tfutils/tfenv)** - Infrastructure as Code
- **[AWS CLI & configuration](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)** - AWS resource management
- **[SSM Plugin for AWS CLI](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)** - For port forwarding through bastion
- **[uv](https://github.com/astral-sh/uv)** - Python package management
- **[Docker](https://docs.docker.com/engine/install/)** - Container runtime
- **[kubectl](https://kubernetes.io/docs/tasks/tools/)** - Kubernetes CLI
- **[Helm](https://helm.sh/docs/intro/install/)** - Kubernetes package manager

### AWS Permissions

You need elevated AWS permissions to deploy the Terraform stack, including:
- EKS cluster management
- VPC and networking resources
- RDS Aurora PostgreSQL
- ElastiCache Redis
- Cognito user pools
- ECR repositories
- IAM roles and policies

### Cost Considerations

**⚠️ Important**: This deployment creates AWS resources that incur costs, including:
- EKS cluster and worker nodes
- Aurora PostgreSQL cluster
- ElastiCache Redis cluster
- Application Load Balancer
- NAT Gateways
- S3 buckets

## Deployment Dependencies

The deployment must follow this specific order due to dependencies:

### Phase 1: Infrastructure Dependencies
1. **VPC and Networking** - Private/public subnets, NAT gateways
2. **EKS Cluster** - Kubernetes control plane and worker nodes
3. **Aurora PostgreSQL** - Database for application data
4. **ElastiCache Redis** - Caching layer
5. **Cognito** - Authentication and authorization
6. **ECR Repositories** - Container image storage

### Phase 2: Database Setup Dependencies
1. **Database Migrations** - Create tables and schema
2. **PostgreSQL Users** - Application-specific database users

### Phase 3: Platform Services Dependencies
1. **LiteLLM Gateway** (REQUIRED) - LLM access proxy
2. **Memory Gateway** (OPTIONAL) - Memory management service
3. **Retrieval Gateway** (OPTIONAL) - Document retrieval service

### Phase 4: Agent Application
1. **Container Build** - Build and push agent container
2. **Helm Deployment** - Deploy agent to Kubernetes
3. **Configuration** - Environment variables and secrets
4. **Testing** - Verify deployment and functionality

## Detailed Deployment Steps

### Step 1: Repository Setup

```bash
# Clone the repository
git clone https://github.com/aws-samples/sample-agentic-platform.git
cd sample-agentic-platform
```

### Step 2: Infrastructure Deployment

#### Option A: Automated Bootstrap (Recommended for Production)
```bash
# Currently Work In Progress (WIP)
cd bootstrap/
# Follow bootstrap/README.md for detailed instructions
```

#### Option B: Manual Deployment (Testing/Development)

**2.1 Foundation Stack (Optional - if no existing VPC)**
```bash
cd infrastructure/stacks/foundation/
terraform init
terraform plan
terraform apply
```

**2.2 Backend Configuration**

Create `backend.tf` in `infrastructure/stacks/platform-eks/`:
```hcl
terraform {
  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "agentic-platform/terraform.tfstate"
    region = "us-west-2"
    encrypt = true
  }
}
```

**2.3 Configure Variables**

Create `terraform.tfvars` in `infrastructure/stacks/platform-eks/`:
```hcl
# Core Configuration
aws_region  = "us-west-2"
environment = "dev"

# Networking (from foundation stack outputs or existing VPC)
vpc_id         = "vpc-xxxxxxxxx"
vpc_cidr_block = "10.0.0.0/16"
private_subnet_ids = [
  "subnet-xxxxxxxxx",
  "subnet-yyyyyyyyy"
]
public_subnet_ids = [
  "subnet-zzzzzzzzz",
  "subnet-aaaaaaaaa"
]

# EKS Access Configuration
enable_eks_public_access = false  # Set to true ONLY for local testing
deploy_inside_vpc = true          # Set to false ONLY for local testing

# Admin Access (replace with your IAM role ARN)
additional_admin_role_arns = [
  "arn:aws:iam::ACCOUNT-ID:role/YourAdminRole"
]
```

**2.4 Deploy Platform Stack**
```bash
cd infrastructure/stacks/platform-eks/
terraform init
terraform plan
terraform apply
```

**2.5 PostgreSQL Users Setup**
```bash
cd infrastructure/stacks/postgres-users/
terraform init
terraform apply
```

### Step 3: EKS Access Configuration

#### For Private EKS Cluster (Recommended)

**3.1 Find Bastion Instance**
```bash
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=*bastion-instance*" "Name=instance-state-name,Values=running" \
  --query "Reservations[].Instances[].InstanceId" \
  --output text)
```

**3.2 Start Port Forwarding**
```bash
aws ssm start-session \
  --target $INSTANCE_ID \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["8080"],"localPortNumber":["8080"]}'
```

**3.3 Configure kubectl (in new terminal)**
```bash
kubectl config set-cluster eks-proxy --server=http://localhost:8080
kubectl config set-credentials eks-proxy-user
kubectl config set-context eks-proxy --cluster=eks-proxy --user=eks-proxy-user
kubectl config use-context eks-proxy
```

**3.4 Verify Access**
```bash
kubectl get nodes
```

### Step 4: Database Setup

```bash
# Run database migrations
./deploy/run-migrations.sh
```

This script automatically:
- Finds the bastion instance and database cluster
- Retrieves credentials from AWS Secrets Manager
- Sets up port forwarding through the bastion
- Runs Alembic migrations
- Cleans up automatically

### Step 5: Deploy Platform Services

#### 5.1 Deploy LiteLLM (REQUIRED)
```bash
./deploy/deploy-litellm.sh
```

**LiteLLM Dependencies:**
- External Secrets Operator for secret management
- Service account with IRSA for AWS access
- ConfigMap for LiteLLM configuration

#### 5.2 Deploy Gateways (OPTIONAL)
```bash
./deploy/deploy-gateways.sh --build
```

This deploys:
- **Memory Gateway**: Configurable provider (bedrock_agentcore or postgres)
- **Retrieval Gateway**: Document retrieval service

**Gateway Configuration:**
- Memory provider can be changed in `k8s/helm/values/applications/memory-gateway-values.yaml`
- Set `MEMORY_PROVIDER` to "bedrock_agentcore" or "postgres"

### Step 6: Deploy Agentic Chat Agent

#### 6.1 Build and Deploy
```bash
./deploy/deploy-application.sh agentic-chat --build
```

This command:
1. **Builds Container**: Uses `src/agentic_platform/agent/agentic_chat/Dockerfile`
2. **Pushes to ECR**: Creates ECR repository if needed
3. **Deploys with Helm**: Uses `k8s/helm/values/applications/agentic-chat-values.yaml`

#### 6.2 Agent Configuration Details

**Container Structure:**
- **Base Image**: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- **Dependencies**: Installed via `requirements.txt`
- **Source Code**: 
  - Core platform: `src/agentic_platform/core/`
  - Tools: `src/agentic_platform/tool/`
  - Agent code: `src/agentic_platform/agent/agentic_chat/`
- **Server**: FastAPI running on port 8080

**Kubernetes Resources:**
- **Deployment**: 1 replica, 100m CPU, 256Mi-512Mi memory
- **Service**: ClusterIP on port 80 → 8080
- **Ingress**: Path `/agentic-chat`
- **ServiceAccount**: `agentic-chat-agent-sa` with IRSA
- **ConfigMap**: Environment variables and endpoints
- **ExternalSecret**: LiteLLM API credentials

**Service Dependencies:**
- **LiteLLM**: `http://litellm.default.svc.cluster.local:80`
- **Memory Gateway**: `http://memory-gateway.default.svc.cluster.local:80`
- **Retrieval Gateway**: `http://retrieval-gateway.default.svc.cluster.local:80`

## Testing the Deployment

### Step 1: Create Test User
```bash
# Get Cognito details from Terraform output
cd infrastructure/stacks/platform-eks
POOL_ID=$(terraform output cognito_user_pool_id | tr -d '"')
CLIENT_ID=$(terraform output cognito_web_client_id | tr -d '"')

# Create test user
uv run python script/create_test_user.py \
  --user-pool-id $POOL_ID \
  --email test@example.com \
  --password "TestPassword123!"
```

### Step 2: Generate Auth Token
```bash
# Generate authentication token
uv run python script/get_auth_token.py \
  --username 'test@example.com' \
  --password 'TestPassword123!' \
  --client-id $CLIENT_ID
```

### Step 3: Test Agent Endpoint
```bash
# Port forward to agent service
kubectl port-forward svc/agentic-chat 8090:80

# Test the chat endpoint
curl -X POST http://localhost:8090/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

## Troubleshooting

### Common Issues

#### 1. LiteLLM Authentication Error
**Error**: `Authentication Error, LiteLLM Virtual Key expected`

**Solution**: 
- Verify External Secrets Operator is running
- Check that the LiteLLM secret is properly synced
- Ensure IRSA role has access to the secret in AWS Secrets Manager

#### 2. Database Connection Issues
**Error**: Cannot connect to PostgreSQL

**Solution**:
- Ensure database migrations have been run: `./deploy/run-migrations.sh`
- Verify port forwarding is active through bastion host
- Check PostgreSQL users stack has been deployed

#### 3. Pod Access Issues
**Error**: Cannot access Kubernetes resources

**Solution**:
- Verify kubectl is configured with port forwarding to bastion host
- Check that your IAM role is in `additional_admin_role_arns`
- Ensure EKS access configuration is correct

#### 4. Container Build Failures
**Error**: Docker build or ECR push fails

**Solution**:
- Verify AWS CLI is configured and authenticated
- Check Docker is running and accessible
- Ensure ECR repository permissions are correct

#### 5. Agent Pod Not Starting
**Error**: Agent pod in CrashLoopBackOff or ImagePullBackOff

**Solution**:
- Check container logs: `kubectl logs -l app=agentic-chat`
- Verify image exists in ECR
- Check service account and IRSA configuration
- Ensure all dependent services (LiteLLM) are running

### Verification Commands

```bash
# Check all pods status
kubectl get pods -A

# Check specific agent
kubectl get pods -l app=agentic-chat
kubectl logs -l app=agentic-chat

# Check services
kubectl get svc

# Check ingress
kubectl get ingress

# Check external secrets
kubectl get externalsecret

# Check service accounts
kubectl get serviceaccount
```

## Cleanup

### Step 1: Remove Kubernetes Resources
```bash
# Uninstall Helm releases
helm uninstall agentic-chat
helm uninstall memory-gateway
helm uninstall retrieval-gateway
helm uninstall litellm

# Remove load balancer controller
helm uninstall lb-controller
```

### Step 2: Remove Infrastructure
```bash
# Remove deletion protection from Aurora
cd infrastructure/stacks/platform-eks/
terraform apply -auto-approve -var="postgres_deletion_protection=false" -target=module.postgres_aurora.aws_rds_cluster.postgres

# Destroy infrastructure
terraform destroy

# Destroy foundation stack (if deployed)
cd ../foundation/
terraform destroy
```

## Security Considerations

### EKS Access Patterns

**✅ Secure (Recommended)**:
- `enable_eks_public_access = false`
- `deploy_inside_vpc = true`
- Access via bastion host with SSM

**✅ Testing Only**:
- `enable_eks_public_access = true`
- `deploy_inside_vpc = false`
- Direct access (sandbox accounts only)

**❌ Invalid Configurations**:
- Both `true` (conflicting)
- Both `false` (no access)

### Best Practices

1. **Never use public EKS access in production**
2. **Use IRSA for service authentication**
3. **Store secrets in AWS Secrets Manager**
4. **Use External Secrets Operator for secret injection**
5. **Enable audit logging and monitoring**
6. **Use least privilege IAM policies**

## Architecture Summary

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User/Client   │───▶│   CloudFront     │───▶│  Load Balancer  │
└─────────────────┘    │   (Optional)     │    │      (ALB)      │
                       └──────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                    EKS Cluster  │                                 │
                       │  ┌─────────────────┐           │    ┌─────────────────┐          │
                       │  │  Agentic Chat   │◀──────────┼───▶│   LiteLLM       │          │
                       │  │     Agent       │           │    │   Gateway       │          │
                       │  └─────────────────┘           │    └─────────────────┘          │
                       │           │                    │             │                   │
                       │           ▼                    │             ▼                   │
                       │  ┌─────────────────┐           │    ┌─────────────────┐          │
                       │  │  Memory         │           │    │  Retrieval      │          │
                       │  │  Gateway        │           │    │  Gateway        │          │
                       │  └─────────────────┘           │    └─────────────────┘          │
                       └─────────────────────────────────┼─────────────────────────────────┘
                                                        │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                     Data Layer  │                                 │
                       │  ┌─────────────────┐           │    ┌─────────────────┐          │
                       │  │   PostgreSQL    │           │    │   ElastiCache   │          │
                       │  │    Aurora       │           │    │     Redis       │          │
                       │  └─────────────────┘           │    └─────────────────┘          │
                       └─────────────────────────────────┼─────────────────────────────────┘
                                                        │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                 Auth & Secrets  │                                 │
                       │  ┌─────────────────┐           │    ┌─────────────────┐          │
                       │  │    Cognito      │           │    │  Secrets        │          │
                       │  │  User Pools     │           │    │  Manager        │          │
                       │  └─────────────────┘           │    └─────────────────┘          │
                       └─────────────────────────────────┼─────────────────────────────────┘
```

This completes the comprehensive deployment guide for the AgentPath framework's `agentic_chat` agent.
