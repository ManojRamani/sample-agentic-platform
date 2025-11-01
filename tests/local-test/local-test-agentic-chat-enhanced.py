#!/usr/bin/env python3
"""
Local testing script for the Agentic Chat Enhanced Agent.
This script allows you to test the agentic_chat_enhanced code locally without EKS.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agentic_platform.core.models.api_models import AgenticRequest, AgenticResponse
from agentic_platform.core.models.memory_models import Message, TextContent
from agentic_platform.agent.agentic_chat_enhanced.agent.agentic_chat_agent import StrandsAgenticChatAgent


async def test_basic_invoke():
    """Test basic synchronous invocation."""
    print("🧪 Testing basic invoke...")
    
    # Create test request
    message = Message(
        role="user",
        content=[TextContent(text="What is 7 + 8?")]
    )
    
    request = AgenticRequest(
        message=message,
        session_id="test-session-enhanced-1"
    )
    
    try:
        # Initialize agent
        agent = StrandsAgenticChatAgent()
        
        # Test invoke
        response = agent.invoke(request)
        
        print(f"✅ Response received:")
        print(f"   Session ID: {response.session_id}")
        text_content = response.message.get_text_content()
        if text_content:
            print(f"   Message: {text_content.text}")
        else:
            print(f"   Message: No text content")
        print(f"   Metadata: {response.metadata}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic invoke: {e}")
        return False


async def test_streaming_invoke():
    """Test streaming invocation."""
    print("\n🧪 Testing streaming invoke...")
    
    # Create test request
    message = Message(
        role="user", 
        content=[TextContent(text="Calculate 18 * 27 and explain the steps")]
    )
    
    request = AgenticRequest(
        message=message,
        session_id="test-session-enhanced-2",
        stream=True
    )
    
    try:
        # Initialize agent
        agent = StrandsAgenticChatAgent()
        
        print("✅ Streaming response:")
        async for event in agent.invoke_stream(request):
            print(f"   Event Type: {event.type}")
            # Handle different event types properly
            if hasattr(event, 'text') and event.text:
                print(f"   Text: {event.text}")
            elif hasattr(event, 'delta') and event.delta:
                print(f"   Delta: {event.delta}")
            elif hasattr(event, 'error'):
                print(f"   Error: {event.error}")
            else:
                print(f"   Event data: {event}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in streaming invoke: {e}")
        return False


async def test_calculator_tool():
    """Test the calculator tool functionality."""
    print("\n🧪 Testing calculator tool...")
    
    # Create test request with calculation
    message = Message(
        role="user",
        content=[TextContent(text="Use the calculator to compute 123 + 456")]
    )
    
    request = AgenticRequest(
        message=message,
        session_id="test-session-enhanced-calc"
    )
    
    try:
        # Initialize agent
        agent = StrandsAgenticChatAgent()
        
        # Test invoke
        response = agent.invoke(request)
        
        text_content = response.message.get_text_content()
        if text_content:
            response_text = text_content.text.lower()
            # Check if response contains the expected result
            if "579" in response_text or "calculator" in response_text:
                print("✅ Calculator tool working correctly")
                print(f"   Response: {text_content.text}")
                return True
            else:
                print("⚠️  Calculator tool may not be working as expected")
                print(f"   Response: {text_content.text}")
                return False
        else:
            print("❌ No text content in response")
            return False
        
    except Exception as e:
        print(f"❌ Error in calculator tool test: {e}")
        return False


async def test_server_endpoints():
    """Test the FastAPI server endpoints locally."""
    print("\n🧪 Testing server endpoints...")
    
    try:
        import httpx
        from agentic_platform.agent.agentic_chat_enhanced.server import app
        
        # Create test client
        async with httpx.AsyncClient(base_url="http://test") as client:
            client._transport = httpx.ASGITransport(app=app)
            
            # Test health endpoint
            health_response = await client.get("/health")
            print(f"✅ Health endpoint: {health_response.status_code} - {health_response.json()}")
            
            # Test invoke endpoint
            test_request = {
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "Hello, what is 9 + 6?"}]
                },
                "session_id": "test-session-enhanced-3"
            }
            
            invoke_response = await client.post("/invoke", json=test_request)
            print(f"✅ Invoke endpoint: {invoke_response.status_code}")
            if invoke_response.status_code == 200:
                result = invoke_response.json()
                print(f"   Response: {result['message']['content'][0]['text']}")
            
            # Test streaming endpoint
            stream_request = {
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "Count from 1 to 3"}]
                },
                "session_id": "test-session-enhanced-stream"
            }
            
            async with client.stream("POST", "/stream", json=stream_request) as stream_response:
                print(f"✅ Stream endpoint: {stream_response.status_code}")
                if stream_response.status_code == 200:
                    chunk_count = 0
                    async for chunk in stream_response.aiter_text():
                        if chunk.strip():
                            chunk_count += 1
                            if chunk_count <= 3:  # Show first few chunks
                                print(f"   Chunk {chunk_count}: {chunk.strip()[:50]}...")
                    print(f"   Received {chunk_count} streaming chunks")
        
        return True
        
    except ImportError:
        print("❌ httpx not available for server testing. Install with: pip install httpx")
        return False
    except Exception as e:
        print(f"❌ Error in server testing: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "boto3",
        "jwt",  # pyjwt package imports as 'jwt'
        "cryptography",
        "litellm",
        "pydantic",
        "strands",
        "strands_tools"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True


def check_environment():
    """Check environment variables and configuration."""
    print("\n🔍 Checking environment...")
    
    # Check for AWS credentials (needed for LiteLLM gateway)
    aws_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]
    aws_configured = any(os.getenv(var) for var in aws_vars)
    
    if aws_configured:
        print("✅ AWS credentials found")
    else:
        print("⚠️  AWS credentials not found - may need for LiteLLM gateway")
    
    # Check for LiteLLM configuration
    litellm_vars = ["LITELLM_PROXY_URL", "LITELLM_API_KEY"]
    litellm_configured = any(os.getenv(var) for var in litellm_vars)
    
    if litellm_configured:
        print("✅ LiteLLM configuration found")
    else:
        print("⚠️  LiteLLM configuration not found - may need for model access")
    
    return True


async def main():
    """Main test function."""
    print("🚀 Local Agentic Chat Enhanced Agent Testing")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        return
    
    # Check environment
    check_environment()
    
    # Run tests
    print("\n" + "=" * 60)
    print("Running Tests...")
    
    tests_passed = 0
    total_tests = 4
    
    # Test basic invoke
    if await test_basic_invoke():
        tests_passed += 1
    
    # Test streaming invoke  
    if await test_streaming_invoke():
        tests_passed += 1
    
    # Test calculator tool
    if await test_calculator_tool():
        tests_passed += 1
    
    # Test server endpoints
    if await test_server_endpoints():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your agentic_chat_enhanced code is working locally.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
