
my account : dpeloyed on local acount 4xxx instead of team-config
my region: us-west-2

vpc-id: vpc-0149ba72dab001634
vpc-name: agent-ptfm-mjramani-vpc

terraform S3-url: s3://mjramani-agents-west/



# Then use it in the modify command
aws eks modify-cluster --name agent-ptfm-eks --region us-west-2 --resources-vpc-config endpointPublicAccess=true,publicAccessCidrs=[76.132.156.127]


## EKS nodes install issue:  [either run this on a bastion right from beginning - or enable your public ip to ocnnect to eks]

my user couldnt access the eks nodes - couldnt see the health

# find your public ip using 

# Check your current public IP
curl -s https://checkip.amazonaws.com


resolution: 

1/ commands to have your public ip open to access the EKS (since you are on the laptop)


# Re-enable public endpoint access
aws eks update-cluster-config --name agent-ptfm-eks --region us-west-2 --resources-vpc-config endpointPublicAccess=true,publicAccessCidrs=["76.132.156.127/32"]


# Check update status - stick both commands together 
aws eks describe-update --name agent-ptfm-eks --region us-west-2 --update-id 04e0430a-617d-3ac8-b62a-ca9629ec2e55

# Or check cluster status
aws eks describe-cluster --name agent-ptfm-eks --region us-west-2 --query 'cluster.status'


once it shows "Successful" and Active (not "Updating")

# Test kubectl connection
kubectl get nodes


should show active ... if yes, 

# Complete Terraform deployment
terraform apply


-- will re-build missing items
## another issue - just kept resetting my publi access - changed infrastructure/stacks/platform-eks/terraform.tfvars

# EKS Access Configuration
enable_eks_public_access = true  # Set to true ONLY for local testing
deploy_inside_vpc = false          # Set to false ONLY for local testing

set public access is true - forced me to make vpc false - check w/ tanner - thats is the only way it worked for me.



# if your temrinal is behaving wierd - commends not seen , but are actually there .... just key in 
reset
- this will reset the terminal , you will not be able to view the word reset :)


aws ssm start-session \
  --target $INSTANCE_ID \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters "portNumber=5432,localPortNumber=5432,host=agent-ptfm-postgres.cluster-c7guemmykggt.us-west-2.rds.amazonaws.com"



# how to install session manager plugin

    # Download the Session Manager plugin
    curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"

    # Install the plugin
    sudo dpkg -i session-manager-plugin.deb

    # Verify installation
    session-manager-plugin



aws ssm start-session \
  --target $INSTANCE_ID \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters "portNumber=5432,localPortNumber=5432,host=agent-ptfm-postgres.cluster-c7guemmykggt.us-west-2.rds.amazonaws.com"


# K8s health checks 

# Quick overview of everything
kubectl get all --all-namespaces

# Check if core components are running
kubectl get pods -n kube-system
kubectl get pods -n external-secrets-system
kubectl get pods -n observability

# Check for any issues
kubectl get events --all-namespaces | grep -i error


# install ocmponents using terraform from remote - operate from witinh bastion


# install code server in bastion host 

## __ecommended Setup: Code-Server__

Here's the complete setup I recommend:

### __1. Install on Bastion:__

```bash
# Connect to bastion
aws ssm start-session --target i-07197f79e99d47926 --region us-west-2

# Install code-server
curl -fsSL https://code-server.dev/install.sh | sh

# Create config directory
mkdir -p ~/.config/code-server

# Create config file
cat > ~/.config/code-server/config.yaml << EOF
bind-addr: 0.0.0.0:8080
auth: password
password: your-secure-password-here
cert: false
EOF

# Start code-server as a service
sudo systemctl enable --now code-server@ubuntu
```

### __2. Access from Local Machine:__

```bash
# Create port forward tunnel
aws ssm start-session --target i-07197f79e99d47926 \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["8080"],"localPortNumber":["8080"]}'

# Open browser to http://localhost:8080
```
so if i ned to know the avilable service-names, where do i look ?

**Checkpoint

Compare

Restore

API Request$0.0524

Great question! Here are the __definitive places__ to find available service names:

## __Method 1: Check Agent Source Code Directory__

```bash
# List all available agent services
ls -la src/agentic_platform/agent/

# This shows directories that contain Dockerfiles for agents
```

## __Method 2: Check Helm Values Files (Most Reliable)__

```bash
# List all available service configurations
ls -la k8s/helm/values/applications/

# Look for files ending in "-values.yaml"
# The service name is the part before "-values.yaml"
```

For example:

- `agentic-chat-values.yaml` → service name: `agentic-chat`
- `langgraph-chat-values.yaml` → service name: `langgraph-chat`
- `memory-gateway-values.yaml` → service name: `memory-gateway`

## __Method 3: Check Docker Directory__

```bash
# Check if there are any services in docker directory
ls -la docker/
```

## __Method 4: Use the Build Script to Discover__

```bash
# Run the build script without a service name to see available options
./deploy/build-container.sh

# Or try a non-existent name to get the error message with available services
./deploy/deploy-application.sh nonexistent --build
```

## __Method 5: Check Both Locations Systematically__

```bash
# Complete discovery command
echo "=== Agent Services ==="
ls -1 src/agentic_platform/agent/ | grep -v __pycache__ | grep -v __init__.py

echo -e "\n=== Helm Values (Available Deployments) ==="
ls -1 k8s/helm/values/applications/ | sed 's/-values.yaml//'

echo -e "\n=== Docker Services ==="
ls -1 docker/ 2>/dev/null || echo "No docker directory services"
```

## __The Golden Rule:__

__The service name must exist in BOTH places:__

1. ✅ __Source code__: `src/agentic_platform/agent/<service-name>/`
2. ✅ __Helm values__: `k8s/helm/values/applications/<service-name>-values.yaml`

## __Quick Reference Command:__

```bash
# One-liner to see all deployable services
ls k8s/helm/values/applications/ | grep -v "^optional" | sed 's/-values.yaml$//' | sort
```

## __From Your Earlier Error:__

The available services shown were:

- `agentic_chat`
- `agentic_rag`
- `langgraph_chat`
- `strands_glue_athena`

But remember to check the __Helm values directory__ as that's the definitive list of what can actually be deployed!

__Pro tip:__ Always check `k8s/helm/values/applications/` - if there's a `<service-name>-values.yaml` file, then `<service-name>` is deployable.


## __Recommended Deployment Order:__

1. __Start with basic agent:__

   ```bash
   ./deploy/deploy-application.sh agentic_chat --build
   ```

2. __Deploy gateways if needed:__

   ```bash
   ./deploy/deploy-gateways.sh --build
   ```

3. __Deploy RAG agent:__

   ```bash
   ./deploy/deploy-application.sh agentic_rag --build
   ```

4. __Deploy LangGraph agent:__

   ```bash
   ./deploy/deploy-application.sh langgraph_chat --build
   ```

## __Check What's Actually Available:__

```bash
# See what agent services exist
ls -la src/agentic_platform/agent/

# See what Helm values files exist
ls -la k8s/helm/values/applications/
```

Try deploying one of the available services like `agentic_chat` first!


# IMP: install docker with buildx enabled 

```
# Check if buildx is available
docker buildx version

# List current builders
docker buildx ls

# Check current context
docker context ls
```
if not , then install it 

```# Install the buildx plugin
sudo apt-get update
sudo apt-get install docker-buildx-plugin

# Verify installation
docker buildx version

# If the above doesn't work, try manual installation:
mkdir -p ~/.docker/cli-plugins
curl -L "https://github.com/docker/buildx/releases/latest/download/buildx-v0.12.1.linux-amd64" -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx

# Test it works
docker buildx version
```



## __Now Let's Deploy Your Agent with Buildx:__

```bash
# 1. Restore the original build script (with buildx support)
cp deploy/build-container.sh.backup deploy/build-container.sh

# 2. Enable BuildKit
export DOCKER_BUILDKIT=1

# 3. Verify the original script is restored
grep "docker.*build" deploy/build-container.sh

# 4. Deploy your agent with full buildx support
./deploy/deploy-application.sh agentic_chat --build
```
# You can get the `<from_tf_output>` values in several ways. Here are the easiest methods:

## __Method 1: From Kubernetes ConfigMap (Easiest)__

(agentic-program-technical-assets) mjramani@SEA:...ample-agentic-platform$ kubectl get configmap agentic-platform-config -o yaml
apiVersion: v1
data:
  AGENT_LITELLM_SECRET_ARN: arn:aws:secretsmanager:us-west-2:423623854297:secret:agent-ptfm-agent-secret-jndNLL
  AGENT_LITELLM_SECRET_NAME: agent-ptfm-agent-secret
  AGENT_ROLE_ARN: arn:aws:iam::423623854297:role/agent-ptfm-agent-role
  AWS_ACCOUNT_ID: "423623854297"
  AWS_DEFAULT_REGION: us-west-2
  AWS_LOAD_BALANCER_CONTROLLER_ROLE_ARN: arn:aws:iam::423623854297:role/agent-ptfm-aws-load-balancer-controller-role
  BASTION_INSTANCE_ID: i-07197f79e99d47926
  BASTION_PRIVATE_IP: 10.0.11.131
  CLUSTER_NAME: agent-ptfm-eks
  COGNITO_DOMAIN: https://dev-auth-f3nk1xc8.auth.us-west-2.amazoncognito.com
  COGNITO_IDENTITY_POOL_ID: us-west-2:6cecab02-c6ac-48dc-9675-50702fa1cb7b
  COGNITO_M2M_CLIENT_ID: 6p2iu7fvrusdauo3pooacnje6g
  COGNITO_PLATFORM_ADMIN_GROUP_NAME: platform_admin
  COGNITO_PLATFORM_USER_GROUP_NAME: platform_user
  COGNITO_SUPER_ADMIN_GROUP_NAME: super_admin
  COGNITO_USER_CLIENT_ID: 3pl0sl5tavr6emafvkhgqgn15s
  COGNITO_USER_POOL_ARN: arn:aws:cognito-idp:us-west-2:423623854297:userpool/us-west-2_MqAL5nQOt
  COGNITO_USER_POOL_ID: us-west-2_MqAL5nQOt
  EKS_CLUSTER_ENDPOINT: https://05D6F7E83547A561647A90B7F471D04F.sk1.us-west-2.eks.amazonaws.com
  EKS_CLUSTER_ID: agent-ptfm-eks
  EKS_CLUSTER_NAME: agent-ptfm-eks
  EKS_NODE_GROUP_ID: agent-ptfm-eks:agent-ptfm-node-group
  ENVIRONMENT: dev
  EXTERNAL_SECRETS_ROLE_ARN: arn:aws:iam::423623854297:role/agent-ptfm-external-secrets-role
  LITELLM_CONFIG_SECRET_ARN: arn:aws:secretsmanager:us-west-2:423623854297:secret:agent-ptfm-litellm-secret-E0Jcvf
  LITELLM_ROLE_ARN: arn:aws:iam::423623854297:role/agent-ptfm-litellm-role
  LITELLM_SECRET_NAME: agent-ptfm-litellm-secret
  LOAD_BALANCER_CONTROLLER_ROLE_ARN: arn:aws:iam::423623854297:role/agent-ptfm-aws-load-balancer-controller-role
  M2M_CREDENTIALS_SECRET_ARN: arn:aws:secretsmanager:us-west-2:423623854297:secret:agent-ptfm-m2mcreds-f3nk1xc8-ldsnsa
  MEMORY_GATEWAY_ROLE_ARN: arn:aws:iam::423623854297:role/agent-ptfm-memory-gateway-role
  OAUTH_TOKEN_ENDPOINT: https://dev-auth-f3nk1xc8.auth.us-west-2.amazoncognito.com/oauth2/token
  OTEL_COLLECTOR_ROLE_ARN: arn:aws:iam::423623854297:role/agent-ptfm-otel-collector-role
  PG_DATABASE: postgres
  PG_PASSWORD_SECRET_ARN: arn:aws:secretsmanager:us-west-2:423623854297:secret:rds!cluster-04b3d562-e698-4cf5-a224-f7b96e512d06-FFZutw
  PG_PORT: "5432"
  PG_READ_ONLY_USER: rdsuser
  PG_READER_ENDPOINT: agent-ptfm-postgres.cluster-ro-c7guemmykggt.us-west-2.rds.amazonaws.com
  PG_USER: rdsuser
  PG_WRITER_ENDPOINT: agent-ptfm-postgres.cluster-c7guemmykggt.us-west-2.rds.amazonaws.com
  POSTGRES_BACKUP_VAULT_NAME: agent-ptfm-pg-vault
  POSTGRES_CLUSTER_ID: agent-ptfm-postgres
  POSTGRES_MASTER_USERNAME: postgres
  POSTGRES_PARAMETER_GROUP_NAME: agent-ptfm-postgres-params
  POSTGRES_SECURITY_GROUP_ID: sg-068e986d671b7ed78
  POSTGRES_SNS_TOPIC_ARN: arn:aws:sns:us-west-2:423623854297:agent-ptfm-postgres-events
  REDIS_HOST: master.agent-ptfm-redis.7dadwf.usw2.cache.amazonaws.com
  REDIS_PASSWORD_SECRET_ARN: arn:aws:secretsmanager:us-west-2:423623854297:secret:agent-ptfm-redis-auth-hj8-8NCvLr
  REDIS_PORT: "6379"
  REGION: us-west-2
  RETRIEVAL_GATEWAY_ROLE_ARN: arn:aws:iam::423623854297:role/agent-ptfm-retrieval-gateway-role
  SPA_DISTRIBUTION_ARN: arn:aws:cloudfront::423623854297:distribution/E3E00J76PFP2F9
  SPA_DISTRIBUTION_ID: E3E00J76PFP2F9
  SPA_DOMAIN_NAME: d6ph8u14pobdv.cloudfront.net
  SPA_WEBSITE_BUCKET_ARN: arn:aws:s3:::terraform-20251026043000597300000001
  SPA_WEBSITE_BUCKET_NAME: terraform-20251026043000597300000001
  SPA_WEBSITE_URL: https://d6ph8u14pobdv.cloudfront.net/frontend
  VPC_ID: vpc-0149ba72dab001634
immutable: false
kind: ConfigMap
metadata:
  creationTimestamp: "2025-10-26T06:06:14Z"
  labels:
    app.kubernetes.io/component: configuration
    app.kubernetes.io/managed-by: terraform
    app.kubernetes.io/name: platform-config
  name: agentic-platform-config
  namespace: default
  resourceVersion: "22088"
  uid: 1d91f847-b2d0-428d-a561-75181cbad7fe





