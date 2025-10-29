# Local Testing Guide for Agentic Chat Agent

This guide provides step-by-step instructions for testing the agentic_chat agent locally on your laptop without requiring EKS deployment.

## Overview

The agentic_chat agent is a FastAPI-based service that uses the Strands framework to provide conversational AI capabilities. This guide shows you how to:

1. Set up your local environment
2. Connect to the deployed LiteLLM service
3. Run comprehensive tests
4. Start the server for development

## Prerequisites

- Python 3.12.8
- Access to the deployed EKS cluster
- `kubectl` configured for the cluster
- `uv` package manager (already installed in this project)

## Step 1: Install Dependencies

```bash
# Navigate to project root
cd /home/mjramani/projects/agents_hub/agent-path/sample-agentic-platform

# Install all project dependencies using uv
uv sync
```

This installs all required packages including:
- fastapi, uvicorn, boto3, pyjwt, cryptography
- litellm, pydantic, strands, strands_tools

## Step 2: Verify EKS Connection

```bash
# Check kubectl connection
kubectl cluster-info

# Verify LiteLLM service is running
kubectl get services | grep litellm
kubectl get pods -l app=litellm
```

Expected output:
```
litellm             ClusterIP   172.20.195.26    <none>        80/TCP    21h
NAME                       READY   STATUS    RESTARTS   AGE
litellm-7876fd6dc5-pjpp6   1/1     Running   0          21h
```

## Step 3: Set Up LiteLLM Connection

### Start Port Forwarding
```bash
# Forward LiteLLM service to localhost:4000
kubectl port-forward service/litellm 4000:80 &
```

### Get LiteLLM API Key
```bash
# Extract the master key from Kubernetes secrets
kubectl get secret litellm-secret -o jsonpath='{.data.LITELLM_MASTER_KEY}' | base64 -d
```

### Test LiteLLM Connection
```bash
# Test with the API key (replace with actual key from previous step)
curl -s http://localhost:4000/health -H "Authorization: Bearer YOUR_API_KEY_HERE"
```

Expected response shows healthy and unhealthy endpoints:
```json
{
  "healthy_endpoints": [
    {"model": "anthropic.claude-3-5-sonnet-20241022-v2:0"},
    {"model": "anthropic.claude-3-5-haiku-20241022-v1:0"}
  ],
  "unhealthy_endpoints": [...],
  "healthy_count": 4,
  "unhealthy_count": 5
}
```

## Step 4: Configure Environment Variables

```bash
# Set LiteLLM configuration (replace with your actual API key)
export LITELLM_KEY="YOUR_API_KEY_FROM_STEP_3"
export LITELLM_API_ENDPOINT="http://localhost:4000"
```

## Step 5: Run Tests

### Option A: Run Comprehensive Test Script
```bash
# Run the automated test suite
python tests/local-test/local-test-agentic-chat.py
```

Expected output:
```
🚀 Local Agentic Chat Agent Testing
==================================================
🔍 Checking dependencies...
✅ fastapi ✅ uvicorn ✅ boto3 ✅ jwt ✅ cryptography 
✅ litellm ✅ pydantic ✅ strands ✅ strands_tools

🧪 Testing basic invoke...
✅ Response received: The result is 4.

🧪 Testing streaming invoke...
✅ Streaming response with real AI conversation

Tests completed: 2/3 passed
```

### Option B: Start Server Manually
```bash
# Start the FastAPI server
cd src/agentic_platform/agent/agentic_chat
python server.py
```

Server starts on port 8003:
```
INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
```

## Step 6: Test Endpoints

### Health Check
```bash
curl http://localhost:8003/health
```

Expected: `{"status":"healthy"}`

### API Documentation
```bash
# Open in browser
open http://localhost:8003/docs
```

### Test Invoke Endpoint
```bash
curl -X POST http://localhost:8003/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": [{"type": "text", "text": "What is 25 * 17?"}]
    },
    "session_id": "test-session"
  }'
```

## Test Results Interpretation

### ✅ Success Indicators
- **Dependencies**: All 9 packages show ✅
- **Basic Invoke**: Returns intelligent AI response with tool usage
- **Streaming**: Shows real-time conversation with Claude 3.5 Sonnet
- **Health Endpoint**: Returns `{"status":"healthy"}`

### ⚠️ Expected "Failures"
- **Server Endpoint Test**: `401 Authentication required` - This is correct behavior
- **Connection Errors**: Only occur if LiteLLM port-forward is not running

## Troubleshooting

### LiteLLM Connection Issues
```bash
# Check if port-forward is running
ps aux | grep "kubectl port-forward"

# Restart port-forward if needed
pkill -f "kubectl port-forward.*litellm"
kubectl port-forward service/litellm 4000:80 &
```

### Dependency Issues
```bash
# Reinstall dependencies
uv sync

# Check specific package
python -c "import jwt; print('PyJWT available')"
```

### EKS Connection Issues
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name agent-ptfm-eks

# Verify connection
kubectl get nodes
```

## Development Workflow

1. **Make Code Changes**: Edit files in `src/agentic_platform/agent/agentic_chat/`
2. **Test Changes**: Run `python tests/local-test/local-test-agentic-chat.py`
3. **Debug**: Start server with `python server.py` and test endpoints
4. **Iterate**: Repeat until satisfied

## Available Models

The deployed LiteLLM service provides access to:

### Healthy Models (Working)
- `anthropic.claude-3-5-sonnet-20241022-v2:0` (Primary)
- `anthropic.claude-3-5-haiku-20241022-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`
- `amazon.titan-embed-text-v2:0`

### Tools Available
- **Calculator**: For mathematical operations
- **Strands Framework**: Full agent capabilities

## Architecture

```
Local Laptop                    EKS Cluster
┌─────────────────┐             ┌──────────────────┐
│ agentic_chat    │             │ LiteLLM Service  │
│ agent (port     │◄────────────┤ (port 80)        │
│ 8003)           │ port-forward │                  │
└─────────────────┘             └──────────────────┘
         │                               │
         │                               │
         ▼                               ▼
┌─────────────────┐             ┌──────────────────┐
│ Test Scripts    │             │ Claude 3.5       │
│ & curl commands │             │ Sonnet & Tools   │
└─────────────────┘             └──────────────────┘
```

## Summary

This setup provides:
- ✅ **Real AI Responses**: Claude 3.5 Sonnet with intelligent answers
- ✅ **Tool Integration**: Calculator and other tools working
- ✅ **Streaming**: Real-time conversation capabilities
- ✅ **Local Development**: Complete laptop-based workflow
- ✅ **Production Infrastructure**: Uses deployed Terraform resources

You now have a fully functional local testing environment for the agentic_chat agent!
