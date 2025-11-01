# Foundation Stack

> **📋 Prerequisites for Viewing Diagrams**
> 
> This README contains Mermaid diagrams for visualizing the architecture and workflows. To view these diagrams properly, please install a Mermaid plugin/extension for your editor or browser:
> 
> - **VS Code**: Install the "Markdown Preview Mermaid Support" extension
> - **GitHub**: Mermaid diagrams are natively supported in GitHub markdown
> - **Browser**: Use the "Mermaid Diagrams" browser extension or view on GitHub
> - **Alternative**: Copy the mermaid code to [mermaid.live](https://mermaid.live) for online rendering

This Terraform stack deploys the foundational infrastructure components required by all other stacks in the Agentic Platform. It provides the core networking and security infrastructure that serves as the foundation for the entire platform.

## Overview

The Foundation stack creates the essential AWS infrastructure components:

- **VPC (Virtual Private Cloud)**: Isolated network environment with public and private subnets
- **Internet Gateway**: Provides internet access to public subnets
- **NAT Gateways**: Enable outbound internet access for private subnets
- **Route Tables**: Control traffic routing within the VPC
- **Security Groups**: Network-level security controls
- **KMS Key**: Optional encryption key for data at rest (when enabled)

## Architecture Overview

```mermaid
graph TB
    subgraph "AWS Region (us-west-2)"
        subgraph "VPC (10.0.0.0/16)"
            subgraph "Availability Zone A"
                PUB1[Public Subnet 1<br/>10.0.1.0/24]
                PRIV1[Private Subnet 1<br/>10.0.3.0/24]
                NAT1[NAT Gateway 1]
            end
            
            subgraph "Availability Zone B"
                PUB2[Public Subnet 2<br/>10.0.2.0/24]
                PRIV2[Private Subnet 2<br/>10.0.4.0/24]
                NAT2[NAT Gateway 2]
            end
            
            IGW[Internet Gateway]
            
            subgraph "Route Tables"
                PUB_RT[Public Route Table]
                PRIV_RT1[Private Route Table 1]
                PRIV_RT2[Private Route Table 2]
            end
            
            subgraph "Security"
                DEFAULT_SG[Default Security Group]
            end
        end
        
        subgraph "KMS (Optional)"
            KMS_KEY[KMS Key<br/>Encryption at Rest]
            KMS_ALIAS[KMS Alias]
        end
    end
    
    subgraph "Internet"
        INTERNET[Internet]
    end
    
    %% Connections
    INTERNET --> IGW
    IGW --> PUB1
    IGW --> PUB2
    
    PUB1 --> NAT1
    PUB2 --> NAT2
    
    NAT1 --> PRIV1
    NAT2 --> PRIV2
    
    %% Route Table Associations
    PUB_RT -.-> PUB1
    PUB_RT -.-> PUB2
    PRIV_RT1 -.-> PRIV1
    PRIV_RT2 -.-> PRIV2
    
    %% KMS relationships
    KMS_KEY --> KMS_ALIAS
    
    %% Styling
    classDef public fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef private fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef gateway fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    classDef routing fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    classDef security fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000
    classDef kms fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#000
    classDef external fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
    
    class PUB1,PUB2 public
    class PRIV1,PRIV2 private
    class IGW,NAT1,NAT2 gateway
    class PUB_RT,PRIV_RT1,PRIV_RT2 routing
    class DEFAULT_SG security
    class KMS_KEY,KMS_ALIAS kms
    class INTERNET external
```

## Component Dependencies

```mermaid
graph TD
    subgraph "Foundation Components"
        VPC[VPC Creation]
        IGW[Internet Gateway]
        PUB_SUBNETS[Public Subnets]
        EIP1[Elastic IP 1]
        EIP2[Elastic IP 2]
        NAT1[NAT Gateway 1]
        NAT2[NAT Gateway 2]
        PRIV_SUBNETS[Private Subnets]
        ROUTE_TABLES[Route Tables]
        SECURITY_GROUPS[Security Groups]
        KMS[KMS Key<br/>Optional]
    end
    
    %% Dependencies
    VPC --> IGW
    VPC --> PUB_SUBNETS
    VPC --> PRIV_SUBNETS
    VPC --> SECURITY_GROUPS
    
    IGW --> PUB_SUBNETS
    PUB_SUBNETS --> EIP1
    PUB_SUBNETS --> EIP2
    EIP1 --> NAT1
    EIP2 --> NAT2
    
    NAT1 --> ROUTE_TABLES
    NAT2 --> ROUTE_TABLES
    IGW --> ROUTE_TABLES
    
    PUB_SUBNETS --> ROUTE_TABLES
    PRIV_SUBNETS --> ROUTE_TABLES
    
    %% KMS is independent
    
    %% Styling
    classDef core fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef network fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef optional fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    
    class VPC,IGW core
    class PUB_SUBNETS,PRIV_SUBNETS,EIP1,EIP2,NAT1,NAT2,ROUTE_TABLES,SECURITY_GROUPS network
    class KMS optional
```

## Prerequisites

Before deploying the Foundation stack, ensure you have:

### 1. AWS Account Setup
- **AWS Account**: Active AWS account with appropriate permissions
- **AWS CLI**: Configured with credentials that have administrative permissions
- **AWS Region**: Choose your target region (default: us-west-2)

### 2. Required Tools
- **Terraform**: Version >= 1.0
- **Git**: For source code management

### 3. AWS Permissions
Your AWS credentials must have permissions for:
- VPC and subnet management
- Internet Gateway and NAT Gateway operations
- Route table and security group management
- Elastic IP allocation and management
- KMS key creation and management (if encryption is enabled)

### 4. Planning Considerations
- **Region Selection**: Choose a region with multiple availability zones
- **CIDR Planning**: Default VPC CIDR is 10.0.0.0/16 (can be customized)
- **Cost Considerations**: NAT Gateways incur hourly charges and data transfer costs
- **Encryption**: Decide whether to enable KMS encryption for downstream services

## Step-by-Step Deployment Guide

### Step 1: Navigate to Foundation Directory

```bash
cd infrastructure/stacks/foundation
```

### Step 2: Create Configuration File

Create a `terraform.tfvars` file with your desired configuration:

```bash
# Create configuration file
vim terraform.tfvars
```

**Example Configuration** (`terraform.tfvars`):
```hcl
########################################################
# Core Configuration
########################################################

aws_region   = "us-west-2"
environment  = "dev"
stack_name   = "agent-platform"

########################################################
# KMS Configuration (Optional)
########################################################

enable_kms_encryption = true
kms_deletion_window   = 7

# Optional: Specify KMS key administrators
# kms_key_administrators = [
#   "arn:aws:iam::123456789012:user/admin-user",
#   "arn:aws:iam::123456789012:role/admin-role"
# ]
```

**Configuration Options:**

The following variables can be configured in your `terraform.tfvars` file. Default values are defined in `variables.tf`:

| Variable | Description | Default (from variables.tf) | Required |
|----------|-------------|------------------------------|----------|
| `aws_region` | AWS region for deployment | `us-west-2` | No |
| `environment` | Environment name (dev, staging, prod) | `dev` | No |
| `stack_name` | Prefix for resource names | `agent-ptfm` | No |
| `enable_kms_encryption` | Enable KMS encryption | `false` | No |
| `kms_deletion_window` | KMS key deletion window (days) | `7` | No |
| `kms_key_administrators` | List of KMS key administrator ARNs | `[]` (empty list) | No |

**Note**: All variables have default values defined in `variables.tf`, so you only need to specify values in `terraform.tfvars` that differ from the defaults.

### Step 3: Initialize Terraform

```bash
terraform init
```

This will:
- Download required Terraform providers
- Initialize the backend
- Prepare the working directory

### Step 4: Plan the Deployment

```bash
terraform plan
```

Review the plan to ensure all resources will be created correctly. You should see:
- 1 VPC
- 4 subnets (2 public, 2 private)
- 1 Internet Gateway
- 2 NAT Gateways
- 2 Elastic IPs
- Route tables and associations
- Security groups
- KMS key and alias (if enabled)

### Step 5: Deploy the Foundation

```bash
terraform apply
```

**What happens during deployment:**

1. **VPC Creation**: A new VPC is created with the specified CIDR block
2. **Subnet Creation**: Public and private subnets are created in two availability zones
3. **Internet Gateway**: Attached to the VPC for public internet access
4. **Elastic IPs**: Allocated for NAT Gateways
5. **NAT Gateways**: Created in public subnets for private subnet internet access
6. **Route Tables**: Configured with appropriate routes for public and private traffic
7. **Security Groups**: Default security group is configured
8. **KMS Key**: Created with alias (if encryption is enabled)

### Step 6: Verify Deployment

```bash
# Check all outputs
terraform output

# Verify VPC creation
aws ec2 describe-vpcs --vpc-ids $(terraform output -raw vpc_id)

# Verify subnets
aws ec2 describe-subnets --subnet-ids $(terraform output -raw public_subnet_ids | tr -d '[]," ')

# Verify NAT Gateways
aws ec2 describe-nat-gateways --nat-gateway-ids $(terraform output -raw nat_gateway_1_id)

# If KMS is enabled, verify KMS key
aws kms describe-key --key-id $(terraform output -raw kms_key_id)
```

### Step 7: Document Outputs for Other Stacks

Save the foundation outputs for use in other stacks:

```bash
# Create a reference file for other stacks
cat > foundation-outputs.txt << EOF
VPC_ID=$(terraform output -raw vpc_id)
VPC_CIDR=$(terraform output -raw vpc_cidr_block)
PUBLIC_SUBNET_IDS=$(terraform output -raw public_subnet_ids)
PRIVATE_SUBNET_IDS=$(terraform output -raw private_subnet_ids)
KMS_KEY_ARN=$(terraform output -raw kms_key_arn)
KMS_KEY_ID=$(terraform output -raw kms_key_id)
EOF

echo "Foundation stack deployed successfully!"
echo "Save these outputs for use in other stacks:"
cat foundation-outputs.txt
```

## Deployment Sequence Diagram

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant TF as Terraform
    participant AWS as AWS Services
    participant VPC as VPC Service
    participant EC2 as EC2 Service
    participant KMS as KMS Service

    Dev->>TF: terraform apply
    
    Note over TF,AWS: Phase 1: Core Network
    TF->>VPC: Create VPC with CIDR 10.0.0.0/16
    VPC-->>TF: VPC created
    
    TF->>VPC: Create Internet Gateway
    VPC-->>TF: IGW created
    
    TF->>VPC: Attach IGW to VPC
    VPC-->>TF: IGW attached
    
    Note over TF,AWS: Phase 2: Subnets
    TF->>VPC: Create public subnets (AZ-a, AZ-b)
    VPC-->>TF: Public subnets created
    
    TF->>VPC: Create private subnets (AZ-a, AZ-b)
    VPC-->>TF: Private subnets created
    
    Note over TF,AWS: Phase 3: NAT Infrastructure
    TF->>EC2: Allocate Elastic IPs
    EC2-->>TF: EIPs allocated
    
    TF->>VPC: Create NAT Gateways in public subnets
    VPC-->>TF: NAT Gateways created
    
    Note over TF,AWS: Phase 4: Routing
    TF->>VPC: Create and configure route tables
    VPC-->>TF: Route tables configured
    
    TF->>VPC: Associate subnets with route tables
    VPC-->>TF: Associations complete
    
    Note over TF,AWS: Phase 5: Security
    TF->>VPC: Configure default security group
    VPC-->>TF: Security group configured
    
    Note over TF,AWS: Phase 6: Encryption (Optional)
    alt KMS Enabled
        TF->>KMS: Create KMS key
        KMS-->>TF: KMS key created
        TF->>KMS: Create KMS alias
        KMS-->>TF: KMS alias created
    end
    
    TF-->>Dev: Foundation deployment complete
```

## Network Architecture Details

### Subnet Design

```mermaid
graph TB
    subgraph "VPC: 10.0.0.0/16 (65,536 IPs)"
        subgraph "Public Subnets (Internet Accessible)"
            PUB1["Public Subnet 1<br/>10.0.1.0/24<br/>254 usable IPs<br/>AZ: us-west-2a"]
            PUB2["Public Subnet 2<br/>10.0.2.0/24<br/>254 usable IPs<br/>AZ: us-west-2b"]
        end
        
        subgraph "Private Subnets (No Direct Internet)"
            PRIV1["Private Subnet 1<br/>10.0.3.0/24<br/>254 usable IPs<br/>AZ: us-west-2a"]
            PRIV2["Private Subnet 2<br/>10.0.4.0/24<br/>254 usable IPs<br/>AZ: us-west-2b"]
        end
        
        subgraph "Reserved Space"
            RESERVED["Available: 10.0.5.0/24 - 10.0.255.0/24<br/>For future expansion"]
        end
    end
    
    %% Styling
    classDef public fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef private fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef reserved fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#000
    
    class PUB1,PUB2 public
    class PRIV1,PRIV2 private
    class RESERVED reserved
```

### Traffic Flow Patterns

```mermaid
graph LR
    subgraph "Internet"
        INTERNET[Internet Traffic]
    end
    
    subgraph "Public Subnets"
        PUB_RESOURCES[Public Resources<br/>Load Balancers<br/>Bastion Hosts]
    end
    
    subgraph "Private Subnets"
        PRIV_RESOURCES[Private Resources<br/>Application Servers<br/>Databases<br/>ECS Tasks]
    end
    
    subgraph "NAT Gateways"
        NAT[NAT Gateways<br/>Outbound Internet Access]
    end
    
    %% Inbound traffic
    INTERNET -->|Inbound| PUB_RESOURCES
    PUB_RESOURCES -->|Internal| PRIV_RESOURCES
    
    %% Outbound traffic
    PRIV_RESOURCES -->|Outbound| NAT
    NAT -->|Outbound| INTERNET
    
    %% Direct outbound from public
    PUB_RESOURCES -->|Direct Outbound| INTERNET
    
    %% Styling
    classDef internet fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000
    classDef public fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef private fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef nat fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    
    class INTERNET internet
    class PUB_RESOURCES public
    class PRIV_RESOURCES private
    class NAT nat
```

## Cost Considerations

### NAT Gateway Costs

NAT Gateways are the primary cost component of the foundation stack:

```mermaid
graph TB
    subgraph "NAT Gateway Costs"
        HOURLY[Hourly Charges<br/>~$0.045/hour per NAT Gateway<br/>~$32.40/month per NAT Gateway]
        DATA[Data Processing<br/>~$0.045/GB processed<br/>Varies by usage]
        TOTAL[Total Monthly Cost<br/>~$64.80 base + data charges<br/>For 2 NAT Gateways]
    end
    
    subgraph "Cost Optimization Options"
        SINGLE[Single NAT Gateway<br/>Reduces cost by 50%<br/>Reduces availability]
        INSTANCE[NAT Instance<br/>Lower cost, more management<br/>Less reliable]
        EGRESS[VPC Endpoints<br/>Reduce data transfer costs<br/>For AWS services]
    end
    
    %% Styling
    classDef cost fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000
    classDef optimization fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    
    class HOURLY,DATA,TOTAL cost
    class SINGLE,INSTANCE,EGRESS optimization
```

## Security Considerations

### Network Security

The foundation stack implements several security best practices:

1. **Network Isolation**: Private subnets have no direct internet access
2. **Controlled Egress**: All outbound traffic from private subnets goes through NAT Gateways
3. **Availability Zone Distribution**: Resources spread across multiple AZs for resilience
4. **Security Groups**: Default security group with minimal permissions

### KMS Encryption

When enabled, the KMS key provides:

- **Data at Rest Encryption**: For RDS, EBS, S3, and other services
- **Key Rotation**: Automatic annual key rotation
- **Access Control**: IAM-based key administration
- **Audit Trail**: CloudTrail logging of key usage

## Troubleshooting Common Issues

### 1. Insufficient Permissions

```bash
# Check your AWS credentials
aws sts get-caller-identity

# Verify permissions
aws iam simulate-principal-policy \
  --policy-source-arn $(aws sts get-caller-identity --query Arn --output text) \
  --action-names ec2:CreateVpc ec2:CreateSubnet ec2:CreateNatGateway \
  --resource-arns "*"
```

### 2. Region Availability Zone Issues

```bash
# Check available AZs in your region
aws ec2 describe-availability-zones --region us-west-2

# Verify NAT Gateway support
aws ec2 describe-availability-zones \
  --region us-west-2 \
  --query 'AvailabilityZones[?State==`available`]'
```

### 3. CIDR Block Conflicts

```bash
# Check existing VPCs in the region
aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,CidrBlock]' --output table

# Verify no CIDR overlap with existing VPCs
```

### 4. NAT Gateway Creation Failures

```bash
# Check Elastic IP limits
aws ec2 describe-account-attributes \
  --attribute-names vpc-max-elastic-ips

# Verify public subnet has internet gateway route
aws ec2 describe-route-tables \
  --filters "Name=association.subnet-id,Values=$(terraform output -raw public_subnet_1_id)"
```

## Updating the Foundation

To update the foundation stack:

```bash
# Update terraform.tfvars with new values
vim terraform.tfvars

# Plan the changes
terraform plan

# Apply the changes
terraform apply
```

**Warning**: Some changes may require resource replacement and could cause downtime for dependent services.

## Cleanup

To remove the foundation stack:

```bash
# Ensure no other stacks depend on this foundation
# Check for resources in the VPC
aws ec2 describe-instances --filters "Name=vpc-id,Values=$(terraform output -raw vpc_id)"

# Destroy the foundation (only if no dependencies exist)
terraform destroy
```

**Critical Warning**: Do not destroy the foundation stack if other stacks (platform-agentcore, agentcore-runtime) are still deployed, as they depend on these resources.

## Outputs Reference

The foundation stack provides the following outputs for use by other stacks:

### Networking Outputs
- `vpc_id`: VPC identifier
- `vpc_cidr_block`: VPC CIDR block
- `public_subnet_ids`: List of public subnet IDs
- `private_subnet_ids`: List of private subnet IDs
- `internet_gateway_id`: Internet Gateway ID
- `nat_gateway_1_id`, `nat_gateway_2_id`: NAT Gateway IDs
- `default_security_group_id`: Default security group ID

### KMS Outputs (if enabled)
- `kms_key_id`: KMS key ID
- `kms_key_arn`: KMS key ARN
- `kms_alias_name`: KMS alias name
- `kms_alias_arn`: KMS alias ARN

### Common Values
- `name_prefix`: Common naming prefix
- `common_tags`: Standard tags applied to all resources
- `aws_region`: Deployment region
- `environment`: Environment name

## Next Steps

After deploying the Foundation stack:

1. **Document Outputs**: Save the foundation outputs for use in other stacks
2. **Deploy Platform Stack**: Deploy either `platform-agentcore` (ECS-based) or `platform-eks` (EKS-based)
3. **Set Up Monitoring**: Configure CloudWatch for VPC Flow Logs and NAT Gateway monitoring
4. **Cost Monitoring**: Set up billing alerts for NAT Gateway usage
5. **Security Review**: Review security groups and NACLs as needed

## Related Documentation

- [Platform AgentCore Stack](../platform-agentcore/README.md)
- [AgentCore Runtime Stack](../agentcore-runtime/README-v2.md)
- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [AWS NAT Gateway Documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
