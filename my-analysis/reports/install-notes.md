#windows power shell

# --1-- Copy from cli

# --2--  get instance id

```
$INSTANCE_ID = aws ec2 describe-instances `
  --filters "Name=tag:Name,Values=*bastion-instance*" "Name=instance-state-name,Values=running" `
  --query "Reservations[].Instances[].InstanceId" `
  --output text

```
## --3-- port forward 

```
aws ssm start-session --target $INSTANCE_ID --document-name AWS-StartPortForwardingSession --parameters '{\"portNumber\":[\"8888\"],\"localPortNumber\":[\"8888\"]}'

```
