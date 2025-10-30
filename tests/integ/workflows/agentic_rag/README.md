# Agentic RAG Integration Tests

This directory contains end-to-end integration tests for the Agentic RAG (Retrieval-Augmented Generation) agent deployed on Amazon EKS.

## Overview

The integration tests validate that the Agentic RAG agent is properly deployed and functioning in the EKS environment with proper authentication mechanisms in place.

## Test File

- `run_agentic_rag_eks_test_with_auth.py` - Main integration test runner with M2M authentication

## What the Tests Cover

### Infrastructure Tests
1. **EKS Cluster Connection** - Verifies connectivity to the Kubernetes cluster
2. **Agentic RAG Service Exists** - Confirms the service is deployed and accessible
3. **Agentic RAG Pods Running** - Validates that pods are running and ready
4. **Service Logs** - Checks that logs are available and contain expected patterns

### API Endpoint Tests (with Authentication)
1. **Health Endpoint** - Tests `/health` endpoint (no auth required)
2. **Ping Endpoint** - Tests `/ping` endpoint (no auth required)
3. **Invoke Endpoint** - Tests `/invoke` endpoint with M2M authentication
4. **Invocations Endpoint** - Tests `/invocations` endpoint with M2M authentication
5. **Streaming Endpoint** - Tests `/stream` endpoint with M2M authentication

## Prerequisites

1. **EKS Cluster Access**: Ensure `kubectl` is configured to access the target EKS cluster
2. **AWS Credentials**: Valid AWS credentials for accessing Secrets Manager
3. **Deployed Service**: The agentic-rag service must be deployed to EKS with the service name `agentic-rag`
4. **M2M Authentication**: Cognito M2M credentials must be configured in AWS Secrets Manager

## Running the Tests

### Basic Execution
```bash
# From the project root directory
python3 tests/integ/workflows/agentic_rag/run_agentic_rag_eks_test_with_auth.py
```

### Expected Output
The tests will output detailed information including:
- Authentication token acquisition
- EKS cluster connectivity status
- Service and pod status
- Complete request/response payloads for API tests
- Test results summary

## Test Configuration

### Port Forwarding
- The tests use port forwarding to access the EKS service locally
- Default port: `8005` (localhost:8005 -> service:80)
- Port forwarding is automatically started and stopped during test execution

### Authentication
- Uses M2M (Machine-to-Machine) authentication via AWS Cognito
- Credentials are retrieved from AWS Secrets Manager
- Default secret ARN: `arn:aws:secretsmanager:us-west-2:423623854297:secret:agent-ptfm-m2mcreds-gci1y867-5UI6p1`

### Test Queries
The tests use RAG-specific queries to validate the agent's functionality:
- "What is retrieval-augmented generation (RAG)?"
- "Explain how vector databases work in RAG systems"
- "What are the benefits of using RAG over traditional language models?"

## Expected Service Behavior

### Successful Response Format
```json
{
    "message": {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "Response about RAG concepts..."
            }
        ],
        "tool_calls": [],
        "tool_results": [],
        "timestamp": 1234567890.123
    },
    "session_id": "test-session-id",
    "metadata": {
        "agent_type": "agentic_rag"
    }
}
```

### Streaming Response
- Content-Type: `text/event-stream`
- Server-Sent Events (SSE) format
- Multiple chunks with event types and data

## Troubleshooting

### Common Issues

1. **Service Not Found**
   - Verify the service is deployed with name `agentic-rag`
   - Check namespace if using non-default namespace

2. **Authentication Failures**
   - Verify AWS credentials have access to Secrets Manager
   - Check that M2M credentials are properly configured
   - Ensure token URL and scopes are correct

3. **Port Forwarding Issues**
   - Check if port 8005 is already in use
   - Verify kubectl has proper cluster access
   - Ensure the service is running and accessible

4. **Pod Not Running**
   - Check pod logs: `kubectl logs -l app=agentic-rag`
   - Verify container image and configuration
   - Check resource limits and node capacity

### Debug Commands
```bash
# Check service status
kubectl get service agentic-rag

# Check pod status
kubectl get pods -l app=agentic-rag

# View pod logs
kubectl logs -l app=agentic-rag --tail=50

# Test port forwarding manually
kubectl port-forward service/agentic-rag 8005:80
```

## Test Results Interpretation

### Success Criteria
- All infrastructure tests pass (EKS, service, pods, logs)
- All API endpoints return 200 status codes
- Authentication works properly
- Responses contain relevant RAG-related content
- Streaming endpoint receives multiple chunks

### Failure Analysis
- Check the detailed output for specific error messages
- Verify service deployment and configuration
- Ensure authentication credentials are valid
- Check network connectivity and port forwarding

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines to validate deployments:

```bash
# Exit code 0 = success, 1 = failure
python3 tests/integ/workflows/agentic_rag/run_agentic_rag_eks_test_with_auth.py
echo "Test exit code: $?"
```

## Related Documentation

- [Agentic RAG Agent Source Code](../../../../src/agentic_platform/agent/agentic_rag/)
- [Deployment Documentation](../../../../DEPLOYMENT.md)
- [Authentication Setup](../../../../bootstrap/)
