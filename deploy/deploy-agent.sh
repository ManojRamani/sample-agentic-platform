#!/bin/bash

# Echo how the script was called
echo "Called: $0 $*"

# Check if agent name is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <agent-name>"
    echo "Example: $0 agentic_chat_enhanced"
    exit 1
fi

AGENT_NAME="$1"

echo "Deploying agent: $AGENT_NAME"
echo "================================"

# Move to project root
cd "$(dirname "$0")/.."

# Step 1: Deploy ECR stack
echo "Step 1: Deploying ECR stack..."
cd infrastructure/stacks/ecr-agent

if [ ! -f "${AGENT_NAME}.tfvars" ]; then
    echo "Error: ${AGENT_NAME}.tfvars not found in infrastructure/stacks/ecr-agent/"
    exit 1
fi

terraform init
terraform apply -var-file="${AGENT_NAME}.tfvars" -auto-approve

if [ $? -ne 0 ]; then
    echo "Error: ECR stack deployment failed"
    exit 1
fi

# Get outputs
ECR_IMAGE_URI=$(terraform output -raw image_uri_latest)
ECR_REPOSITORY=$(terraform output -raw repository_url)

echo "ECR Image URI: $ECR_IMAGE_URI"
echo "ECR Repository: $ECR_REPOSITORY"

# Step 2: Update and deploy Agent-Core runtime
echo ""
echo "Step 2: Deploying Agent-Core runtime..."
cd ../agentcore-runtime

if [ ! -f "${AGENT_NAME}.tfvars" ]; then
    echo "Error: ${AGENT_NAME}.tfvars not found in infrastructure/stacks/agentcore-runtime/"
    exit 1
fi

# Update the tfvars file with the actual ECR URI
sed -i.bak "s|PLACEHOLDER_ECR_URI|$ECR_IMAGE_URI|g" "${AGENT_NAME}.tfvars"

terraform init
terraform apply -var-file="${AGENT_NAME}.tfvars" -auto-approve

if [ $? -ne 0 ]; then
    echo "Error: Agent-Core runtime deployment failed"
    # Restore backup
    mv "${AGENT_NAME}.tfvars.bak" "${AGENT_NAME}.tfvars"
    exit 1
fi

# Step 3: Update and deploy EKS
echo ""
echo "Step 3: Deploying to EKS..."
cd ../../../k8s

# Convert underscores to hyphens for Helm values file
HELM_AGENT_NAME="${AGENT_NAME//_/-}"

if [ ! -f "helm/values/applications/${HELM_AGENT_NAME}-values.yaml" ]; then
    echo "Error: helm/values/applications/${HELM_AGENT_NAME}-values.yaml not found"
    exit 1
fi

# Update the K8s values file with the ECR repository
sed -i.bak "s|PLACEHOLDER_ECR_REPOSITORY|$ECR_REPOSITORY|g" "helm/values/applications/${HELM_AGENT_NAME}-values.yaml"

helm upgrade --install "$HELM_AGENT_NAME" ./helm/charts/agentic-service \
  -f "./helm/values/applications/${HELM_AGENT_NAME}-values.yaml" \
  --namespace default

if [ $? -ne 0 ]; then
    echo "Error: EKS deployment failed"
    # Restore backup
    mv "helm/values/applications/${HELM_AGENT_NAME}-values.yaml.bak" "helm/values/applications/${HELM_AGENT_NAME}-values.yaml"
    exit 1
fi

echo ""
echo "================================"
echo "Deployment complete!"
echo "Agent: $AGENT_NAME"
echo "ECR Repository: $ECR_REPOSITORY"
echo "ECR Image URI: $ECR_IMAGE_URI"
echo ""
echo "Services deployed:"
echo "- ECR Repository: agentic-platform-${AGENT_NAME}"
echo "- Agent-Core Runtime: ${AGENT_NAME}"
echo "- EKS Service: ${HELM_AGENT_NAME}"
echo ""
echo "Access points:"
echo "- Agent-Core: Check AWS Console for runtime endpoint"
echo "- EKS: http://your-cluster-endpoint/${HELM_AGENT_NAME//_/-}"
