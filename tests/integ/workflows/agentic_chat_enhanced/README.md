# Agentic Chat Enhanced Agent Integration Tests

This directory contains integration tests for the `agentic_chat_enhanced` agent deployed on different runtime environments.

## Test Files

### 1. `run_agentic_chat_enhanced_eks_test_with_auth.py`
**Purpose**: End-to-end testing of the agentic_chat_enhanced agent deployed on EKS runtime.

**Features**:
- Tests EKS cluster connectivity
- Validates service and pod deployment
- Tests health endpoint (no authentication required)
- Tests invoke endpoint with M2M authentication
- Tests streaming endpoint with M2M authentication
- Validates service logs
- Uses port forwarding for local testing

**Usage**:
```bash
cd /path/to/sample-agentic-platform
python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_eks_test_with_auth.py
```

**Prerequisites**:
- kubectl configured for EKS cluster access
- AWS credentials configured
- agentic-chat-enhanced service deployed on EKS
- M2M credentials available in AWS Secrets Manager

### 2. `run_agentic_chat_enhanced_agentcore_test.py`
**Purpose**: End-to-end testing of the agentic_chat_enhanced agent deployed on AWS Bedrock Agent-Core runtime.

**Features**:
- Tests Agent-Core runtime existence and status
- Tests Agent-Core memory existence and status
- Tests runtime invocation with calculator tool
- Tests streaming runtime invocation
- Tests memory operations
- Uses AWS Bedrock Agent Runtime client

**Usage**:
```bash
cd /path/to/sample-agentic-platform
python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_agentcore_test.py
```

**Prerequisites**:
- AWS credentials configured with Bedrock Agent permissions
- agentic_chat_enhanced runtime deployed on Agent-Core
- Runtime ARN and Memory ARN available

## Test Architecture

### Authentication
- **EKS Tests**: Use Cognito M2M token authentication
- **Agent-Core Tests**: Use AWS IAM credentials and Bedrock Agent Runtime API

### Test Data
Both test suites use calculator-based test cases to validate:
- Basic arithmetic operations (addition, multiplication)
- Tool usage (calculator tool integration)
- Response validation
- Streaming capabilities

### Error Handling
- Comprehensive error reporting
- Graceful failure handling
- Detailed logging for debugging
- Test result summaries

## Runtime Information

### EKS Deployment
- **Service**: `agentic-chat-enhanced`
- **Port**: 80 (forwarded to localhost:8004 for testing)
- **Endpoints**: `/health`, `/invoke`, `/stream`
- **Authentication**: Bearer token required for `/invoke` and `/stream`

### Agent-Core Deployment
- **Runtime ARN**: `arn:aws:bedrock-agentcore:us-west-2:423623854297:runtime/gzvb_agentic_chat_enhanced-iz4x0b5CM1`
- **Memory ARN**: `arn:aws:bedrock-agentcore:us-west-2:423623854297:memory/agentic_chat_enhanced_memory_v2-IFCnfI37Mb`
- **Region**: us-west-2
- **API**: AWS Bedrock Agent Runtime

## Expected Test Results

### Successful Test Run
```
🚀 EKS Integration Tests for Agentic Chat Enhanced Agent (With Auth)
================================================================================
✅ PASS EKS Cluster Connection
✅ PASS Agentic Chat Enhanced Service Exists
✅ PASS Agentic Chat Enhanced Pods Running
✅ PASS Service Logs
✅ PASS Health Endpoint (No Auth)
✅ PASS Invoke Endpoint (With Auth)
✅ PASS Streaming Endpoint (With Auth)

Results: 7/7 tests passed
🎉 All EKS integration tests passed!
```

### Test Validation
Tests validate:
- Service availability and health
- Authentication mechanisms
- Calculator tool functionality
- Response content accuracy
- Streaming capabilities
- Error handling

## Troubleshooting

### Common Issues

1. **EKS Connection Issues**
   - Verify kubectl configuration: `kubectl cluster-info`
   - Check EKS cluster access permissions

2. **Authentication Failures**
   - Verify M2M credentials in AWS Secrets Manager
   - Check token expiration and refresh

3. **Service Not Found**
   - Verify deployment: `kubectl get svc agentic-chat-enhanced`
   - Check pod status: `kubectl get pods -l app=agentic-chat-enhanced`

4. **Agent-Core Runtime Issues**
   - Verify runtime deployment in AWS Console
   - Check IAM permissions for Bedrock Agent access
   - Validate runtime ARN and status

### Debug Commands

```bash
# Check EKS deployment
kubectl get all -l app=agentic-chat-enhanced

# Check pod logs
kubectl logs -l app=agentic-chat-enhanced --tail=50

# Test port forwarding manually
kubectl port-forward service/agentic-chat-enhanced 8004:80

# Check Agent-Core runtime status
aws bedrock-agentcore get-runtime --runtime-id gzvb_agentic_chat_enhanced-iz4x0b5CM1 --region us-west-2
```

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines for:
- Post-deployment validation
- Regression testing
- Performance monitoring
- Health checks

Example usage in deployment pipeline:
```bash
# Deploy agent
./deploy/deploy-agent.sh agentic_chat_enhanced

# Run integration tests
python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_eks_test_with_auth.py
python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_agentcore_test.py
