# Testing Guide for Agentic Chat Enhanced Agent

This document provides a comprehensive guide for testing the `agentic_chat_enhanced` agent across all deployment environments.

## Overview

The `agentic_chat_enhanced` agent has been deployed with a comprehensive testing strategy that validates functionality across three key areas:

1. **Local Testing** - Validates agent code functionality without external dependencies
2. **EKS Runtime Testing** - End-to-end testing on Kubernetes deployment
3. **Agent-Core Runtime Testing** - End-to-end testing on AWS Bedrock Agent-Core

## Test Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Testing Strategy                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Local Testing  │  │  EKS Testing    │  │ Agent-Core Test │  │
│  │                 │  │                 │  │                 │  │
│  │ • Agent Logic   │  │ • K8s Service   │  │ • Runtime API   │  │
│  │ • Tool Usage    │  │ • Auth Flow     │  │ • Memory Ops    │  │
│  │ • Streaming     │  │ • Port Forward  │  │ • Streaming     │  │
│  │ • FastAPI       │  │ • Health Check  │  │ • Tool Invoke   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Test Files and Locations

### 1. Local Testing
**File**: `tests/local-test/local-test-agentic-chat-enhanced.py`

**Purpose**: Validates the agent code works correctly in isolation

**Test Coverage**:
- ✅ Basic synchronous invocation
- ✅ Streaming invocation
- ✅ Calculator tool functionality
- ✅ FastAPI server endpoints
- ✅ Dependency validation
- ✅ Environment configuration

### 2. EKS Integration Testing
**File**: `tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_eks_test_with_auth.py`

**Purpose**: End-to-end validation of EKS deployment with authentication

**Test Coverage**:
- ✅ EKS cluster connectivity
- ✅ Service and pod deployment validation
- ✅ Health endpoint testing (no auth)
- ✅ Invoke endpoint with M2M authentication
- ✅ Streaming endpoint with M2M authentication
- ✅ Service logs validation
- ✅ Port forwarding functionality

### 3. Agent-Core Integration Testing
**File**: `tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_agentcore_test.py`

**Purpose**: End-to-end validation of Agent-Core deployment

**Test Coverage**:
- ✅ Runtime existence and status
- ✅ Memory existence and status
- ✅ Runtime invocation with tools
- ✅ Streaming runtime invocation
- ✅ Memory operations
- ✅ AWS Bedrock Agent Runtime API

## Running the Tests

### Prerequisites

#### All Tests
```bash
# Install required dependencies
pip install boto3 httpx requests asyncio

# Set up AWS credentials
aws configure
# or
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-west-2
```

#### EKS Tests Additional Requirements
```bash
# Configure kubectl for EKS cluster
aws eks update-kubeconfig --region us-west-2 --name your-cluster-name

# Verify cluster access
kubectl cluster-info
```

### Test Execution

#### 1. Local Testing
```bash
cd /path/to/sample-agentic-platform
python tests/local-test/local-test-agentic-chat-enhanced.py
```

**Expected Output**:
```
🚀 Local Agentic Chat Enhanced Agent Testing
============================================================
🔍 Checking dependencies...
✅ fastapi
✅ uvicorn
✅ boto3
✅ jwt
✅ cryptography
✅ litellm
✅ pydantic
✅ strands
✅ strands_tools

🔍 Checking environment...
✅ AWS credentials found
✅ LiteLLM configuration found

============================================================
Running Tests...
🧪 Testing basic invoke...
✅ Response received:
   Session ID: test-session-enhanced-1
   Message: 7 + 8 = 15
   Metadata: {'agent_type': 'strands_agentic_chat'}

🧪 Testing streaming invoke...
✅ Streaming response:
   Event Type: text_delta
   Delta: I'll calculate 18 * 27 step by step...

🧪 Testing calculator tool...
✅ Calculator tool working correctly
   Response: Using the calculator: 123 + 456 = 579

🧪 Testing server endpoints...
✅ Health endpoint: 200 - {'status': 'healthy'}
✅ Invoke endpoint: 200
   Response: 9 + 6 = 15
✅ Stream endpoint: 200
   Received 15 streaming chunks

============================================================
Tests completed: 4/4 passed
🎉 All tests passed! Your agentic_chat_enhanced code is working locally.
```

#### 2. EKS Integration Testing
```bash
cd /path/to/sample-agentic-platform
python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_eks_test_with_auth.py
```

**Expected Output**:
```
🚀 EKS Integration Tests for Agentic Chat Enhanced Agent (With Auth)
================================================================================

🔐 Getting M2M authentication token...
   Token URL: https://your-cognito-domain/oauth2/token
   Client ID: your-client-id
   Scopes: your-scopes
✅ M2M token obtained (expires in 3600 seconds)

🔍 Testing EKS cluster connection...
✅ EKS cluster connection successful

🔍 Testing agentic-chat-enhanced service exists...
✅ Service exists: agentic-chat-enhanced
   Type: ClusterIP, IP: 172.20.131.61, Port: 80

🔍 Testing agentic-chat-enhanced pods are running...
✅ Pod agentic-chat-enhanced-7c9bf95c76-kvg7h: Running (1/1 ready)

🔍 Testing service logs...
✅ Service logs available
✅ Found expected log patterns: ['uvicorn', 'started server', 'health']

🔍 Starting port forwarding...
✅ Port forwarding started (localhost:8004 -> service:80)

🔍 Testing health endpoint...
✅ Health endpoint: 200 - healthy

🔍 Testing invoke endpoint with authentication...
   📤 REQUEST PAYLOAD:
   {
       "message": {
           "role": "user",
           "content": [{"type": "text", "text": "What is 35 + 47? Use the calculator tool."}]
       },
       "session_id": "eks-integration-test-enhanced-auth"
   }
   📥 RESPONSE STATUS: 200
✅ Invoke endpoint: 200
   📝 EXTRACTED RESPONSE TEXT:
   Using the calculator tool: 35 + 47 = 82
✅ Response contains expected calculation result

🔍 Testing streaming endpoint with authentication...
   Response status: 200
✅ Streaming endpoint: 200
   Content-Type: text/plain; charset=utf-8
✅ Received 12 streaming chunks

🔧 Stopping port forwarding...

================================================================================
TEST SUMMARY
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

#### 3. Agent-Core Integration Testing
```bash
cd /path/to/sample-agentic-platform
python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_agentcore_test.py
```

**Expected Output**:
```
🚀 Agent-Core Integration Tests for Agentic Chat Enhanced Agent
================================================================================
🔧 Setting up AWS clients...
✅ AWS Bedrock Agent Runtime client initialized

🔍 Getting runtime information from Terraform outputs...
✅ Runtime ARN: arn:aws:bedrock-agentcore:us-west-2:423623854297:runtime/gzvb_agentic_chat_enhanced-iz4x0b5CM1
✅ Runtime Endpoint ARN: arn:aws:bedrock-agentcore:us-west-2:423623854297:runtime/gzvb_agentic_chat_enhanced-iz4x0b5CM1/runtime-endpoint/gzvb_agentic_chat_enhancedEndpoint
✅ Memory ARN: arn:aws:bedrock-agentcore:us-west-2:423623854297:memory/agentic_chat_enhanced_memory_v2-IFCnfI37Mb

🔍 Testing Agent-Core runtime exists...
✅ Runtime exists: agentic_chat_enhanced
   Status: Active
   Runtime ID: gzvb_agentic_chat_enhanced-iz4x0b5CM1

🔍 Testing Agent-Core memory exists...
✅ Memory exists: agentic_chat_enhanced_memory_v2
   Status: Active
   Memory ID: agentic_chat_enhanced_memory_v2-IFCnfI37Mb

🔍 Testing Agent-Core memory operations...
✅ Memory operations successful
   Memory Name: agentic_chat_enhanced_memory_v2
   Memory Type: VECTOR

🔍 Testing Agent-Core runtime invocation...
   📤 REQUEST:
   Runtime ID: gzvb_agentic_chat_enhanced-iz4x0b5CM1
   Message: What is 45 + 37? Please use the calculator tool.
   📥 RESPONSE:
   Chunk: I'll help you calculate 45 + 37 using the calc...
   Chunk: ulator tool. Let me do that for you...
✅ Runtime invocation successful
   📝 COMPLETE RESPONSE:
   I'll help you calculate 45 + 37 using the calculator tool. The result is 82.
✅ Response contains expected calculation result

🔍 Testing Agent-Core runtime streaming invocation...
   📤 STREAMING REQUEST:
   Runtime ID: gzvb_agentic_chat_enhanced-iz4x0b5CM1
   Message: Calculate 15 * 23 step by step using the calculator
✅ Streaming invocation started
   Chunk 1: I'll calculate 15 * 23 step by step using the...
   Chunk 2: calculator tool. Let me perform this multipli...
   Chunk 3: cation for you. The result is 345.
✅ Received 8 streaming chunks
   📝 COMPLETE STREAMING RESPONSE:
   I'll calculate 15 * 23 step by step using the calculator tool. The result is 345.

================================================================================
TEST SUMMARY
================================================================================
✅ PASS Runtime Exists
✅ PASS Memory Exists
✅ PASS Memory Operations
✅ PASS Runtime Invocation
✅ PASS Streaming Runtime Invocation

Results: 5/5 tests passed
🎉 All Agent-Core integration tests passed!
```

## Test Validation Criteria

### Functional Validation
- ✅ **Calculator Tool**: All tests validate calculator tool usage with arithmetic operations
- ✅ **Response Accuracy**: Tests check for expected numerical results (82, 345, etc.)
- ✅ **Streaming**: Validates streaming responses with chunk counting
- ✅ **Authentication**: EKS tests validate M2M token authentication flow
- ✅ **Health Checks**: Service health and readiness validation

### Performance Validation
- ✅ **Response Time**: Tests include timeout handling (10-30 seconds)
- ✅ **Streaming Latency**: Chunk-by-chunk response validation
- ✅ **Connection Stability**: Port forwarding and connection management

### Error Handling Validation
- ✅ **Authentication Failures**: 401 error handling
- ✅ **Connection Errors**: Network timeout and connection error handling
- ✅ **Service Unavailability**: Graceful failure when services are down
- ✅ **Invalid Requests**: Malformed request handling

## Troubleshooting Guide

### Common Issues and Solutions

#### Local Testing Issues
```bash
# Missing dependencies
pip install fastapi uvicorn boto3 httpx requests pydantic strands strands_tools

# AWS credentials not configured
aws configure
# or set environment variables

# LiteLLM configuration missing
export LITELLM_PROXY_URL=your_proxy_url
export LITELLM_API_KEY=your_api_key
```

#### EKS Testing Issues
```bash
# kubectl not configured
aws eks update-kubeconfig --region us-west-2 --name your-cluster

# Service not found
kubectl get svc agentic-chat-enhanced
kubectl get pods -l app=agentic-chat-enhanced

# Port forwarding issues
kubectl port-forward service/agentic-chat-enhanced 8004:80

# Authentication token issues
# Check AWS Secrets Manager for M2M credentials
aws secretsmanager get-secret-value --secret-id agent-ptfm-m2mcreds-gci1y867-5UI6p1
```

#### Agent-Core Testing Issues
```bash
# Runtime not found
aws bedrock-agentcore get-runtime --runtime-id gzvb_agentic_chat_enhanced-iz4x0b5CM1 --region us-west-2

# Permissions issues
# Ensure IAM role has bedrock-agentcore permissions

# Memory access issues
aws bedrock-agentcore get-memory --memory-id agentic_chat_enhanced_memory_v2-IFCnfI37Mb --region us-west-2
```

## Integration with CI/CD

### Pipeline Integration
```yaml
# Example GitHub Actions workflow
name: Test Agentic Chat Enhanced Agent
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install boto3 httpx requests
          
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
          
      - name: Run local tests
        run: python tests/local-test/local-test-agentic-chat-enhanced.py
        
      - name: Configure kubectl
        run: aws eks update-kubeconfig --region us-west-2 --name your-cluster
        
      - name: Run EKS integration tests
        run: python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_eks_test_with_auth.py
        
      - name: Run Agent-Core integration tests
        run: python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_agentcore_test.py
```

### Deployment Validation
```bash
#!/bin/bash
# Post-deployment validation script

echo "🚀 Starting post-deployment validation..."

# Deploy the agent
./deploy/deploy-agent.sh agentic_chat_enhanced

# Wait for deployment to stabilize
sleep 30

# Run all tests
echo "Running local tests..."
python tests/local-test/local-test-agentic-chat-enhanced.py

echo "Running EKS integration tests..."
python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_eks_test_with_auth.py

echo "Running Agent-Core integration tests..."
python tests/integ/workflows/agentic_chat_enhanced/run_agentic_chat_enhanced_agentcore_test.py

echo "✅ All tests completed successfully!"
```

## Test Maintenance

### Regular Updates
- **Monthly**: Update test data and expected responses
- **Per Release**: Validate new features and functionality
- **Quarterly**: Review and update authentication mechanisms
- **As Needed**: Update runtime ARNs and configuration

### Monitoring and Alerts
- Set up alerts for test failures in CI/CD
- Monitor test execution times for performance regression
- Track test coverage and add tests for new features
- Regular review of test logs for improvement opportunities

## Conclusion

The comprehensive testing strategy for `agentic_chat_enhanced` ensures:

1. **Code Quality**: Local tests validate core functionality
2. **Deployment Validation**: Integration tests confirm successful deployments
3. **End-to-End Functionality**: Full workflow testing across both runtimes
4. **Authentication Security**: Proper authentication flow validation
5. **Performance Monitoring**: Response time and streaming validation
6. **Error Handling**: Comprehensive error scenario coverage

This testing framework provides confidence in the agent's functionality across all deployment environments and supports continuous integration and deployment practices.
