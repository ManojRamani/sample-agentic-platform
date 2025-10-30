# LangGraph Chat Agent EKS Integration Tests

This directory contains end-to-end integration tests for the LangGraph Chat Agent deployed on Amazon EKS.

## Test File

**`run_langgraph_chat_eks_test_with_auth.py`** - Complete EKS integration test with authentication support

This is the **production-ready** test that includes:
- ✅ **Machine-to-Machine (M2M) authentication** using AWS Cognito
- ✅ **Complete end-to-end testing** (9/9 tests pass)
- ✅ **Real-world authentication scenarios**
- ✅ **Comprehensive test coverage**

## Usage

```bash
# Run the authenticated EKS integration test
python run_langgraph_chat_eks_test_with_auth.py
```

## Prerequisites

1. **EKS Cluster Access**: Ensure `kubectl` is configured for your EKS cluster
2. **LangGraph Chat Service**: The `langgraph-chat` service must be deployed on EKS
3. **AWS Credentials**: Required for M2M token authentication
4. **Dependencies**: Install required packages:
   ```bash
   pip install httpx boto3 asyncio
   ```

## Test Coverage

### Infrastructure Tests
- ✅ EKS cluster connectivity
- ✅ LangGraph Chat service existence and configuration
- ✅ Pod health and readiness status
- ✅ Service logs and activity monitoring

### Authentication Tests
- ✅ M2M token retrieval from AWS Secrets Manager
- ✅ JWT token validation and refresh
- ✅ Authenticated API access

### API Endpoint Tests
- ✅ `/health` - Health check endpoint
- ✅ `/ping` - Ping endpoint  
- ✅ `/chat` - Main chat interface
- ✅ `/invocations` - Alternative chat endpoint

### Functional Tests
- ✅ **Simple queries** (e.g., "What is 35 + 47?")
- ✅ **Knowledge queries** (e.g., "What is the capital of Japan?")
- ✅ **Complex queries** (e.g., "Explain machine learning vs AI")
- ✅ **Response validation** and intelligent content verification

## Test Results

When working correctly, you should see:
```
🚀 EKS Integration Tests for LangGraph Chat Agent (with Auth)
============================================================
✅ PASS EKS Cluster Connection
✅ PASS LangGraph Chat Service Exists  
✅ PASS LangGraph Chat Pods Running
✅ PASS Service Configuration
✅ PASS Service Logs
✅ PASS M2M Token Authentication
✅ PASS Health Endpoint
✅ PASS Chat Endpoint
✅ PASS Complex Query

Results: 9/9 tests passed
🎉 All EKS integration tests passed!
```

## Troubleshooting

### Common Issues
- **kubectl not configured**: Ensure your kubeconfig points to the correct EKS cluster
- **Service not found**: Verify the `langgraph-chat` service is deployed
- **Authentication failures**: Check AWS credentials and Secrets Manager access
- **Port forwarding issues**: The test automatically manages port forwarding to localhost:8004

### Debug Commands
```bash
# Check EKS connection
kubectl cluster-info

# Check service status
kubectl get service langgraph-chat

# Check pod status  
kubectl get pods -l app=langgraph-chat

# View service logs
kubectl logs -l app=langgraph-chat --tail=20
```

## Architecture

The test uses **port forwarding** to securely access the EKS service:
```
Test → kubectl port-forward → EKS Service → LangGraph Chat Pods
```

This approach:
- ✅ Works with private EKS clusters
- ✅ Doesn't require LoadBalancer or Ingress setup
- ✅ Uses secure kubectl authentication
- ✅ Tests the actual deployed service (not mocks)

## Previous Files (Removed)

The following files were removed as they are redundant:
- ~~`run_langgraph_chat_eks_test.py`~~ - No authentication support (6/10 tests passed)
- ~~`test_langgraph_chat_eks.py`~~ - Pytest version without authentication

The authenticated version (`run_langgraph_chat_eks_test_with_auth.py`) provides all the same functionality plus production-ready authentication, making it the single source of truth for EKS integration testing.
