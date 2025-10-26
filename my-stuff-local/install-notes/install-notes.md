
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











