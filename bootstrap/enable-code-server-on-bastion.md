I'll provide step-by-step instructions for accessing the code server on the bastion host via port forwarding. This allows you to have a complete development environment running within your VPC.

## Step-by-Step Instructions: Access Code Server on Bastion Host

### Prerequisites
- Your EKS infrastructure is deployed with a bastion host
- You have AWS CLI configured with appropriate permissions
- You have Session Manager plugin installed

### Step 1: Get the Bastion Instance ID
```bash
# Find your bastion instance
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=*bastion-instance*" "Name=instance-state-name,Values=running" \
  --query "Reservations[].Instances[].InstanceId" \
  --output text)

echo "Bastion Instance ID: $INSTANCE_ID"
```

### Step 2: Start Port Forwarding Session
```bash
# Forward local port 8888 to bastion host port 8888
aws ssm start-session \
  --target $INSTANCE_ID \
  --document-name AWS-StartPortForwardingSession \
  --parameters "portNumber=8888,localPortNumber=8888"
```

### Step 3: Access Code Server
1. Open your web browser
2. Navigate to: `http://localhost:8888`
3. You should see the code server interface running within your VPC

### Step 4: Using the Development Environment
Once connected, you'll have:
- Full VS Code interface in your browser
- Access to all VPC resources (databases, EKS cluster, etc.)
- Terminal access within the VPC
- Ability to run kubectl commands directly
- File editing and project management capabilities

### Step 5: Stop the Session (When Done)
- Press `Ctrl+C` in the terminal where you started the port forwarding
- Or close the terminal window

## Benefits of This Approach
- **Secure**: Development environment runs within your VPC
- **No Public Access Needed**: Works even with private EKS clusters
- **Full Access**: Can reach all internal resources (RDS, ElastiCache, etc.)
- **Persistent**: Files and configurations persist on the bastion host

## Troubleshooting
- If port 8888 is busy locally, use a different port: `localPortNumber=8889`
- Ensure your bastion host has the code server installed and running
- Check security groups allow port 8888 traffic

Would you like me to help you implement this setup or troubleshoot any specific issues?