#!/usr/bin/env python3
"""
Local testing script for the LangGraph Chat Agent.
This script allows you to test the langgraph_chat code locally without EKS.
"""

# CRITICAL: Set environment to 'local' BEFORE any imports to disable authentication middleware
import os
os.environ["ENVIRONMENT"] = "local"

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agentic_platform.core.models.api_models import AgenticRequest, AgenticResponse
from agentic_platform.core.models.memory_models import Message, TextContent
from agentic_platform.agent.langgraph_chat.chat_controller import ChatController


async def test_basic_invoke():
    """Test basic synchronous invocation."""
    print("🧪 Testing basic invoke...")
    
    # Create test request
    message = Message(
        role="user",
        content=[TextContent(text="What is 2 + 2?")]
    )
    
    request = AgenticRequest(
        message=message,
        session_id="test-session-1"
    )
    
    try:
        # Test invoke using the controller
        response = ChatController.chat(request)
        
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
        import traceback
        traceback.print_exc()
        return False


async def test_complex_query():
    """Test with a more complex query."""
    print("\n🧪 Testing complex query...")
    
    # Create test request
    message = Message(
        role="user", 
        content=[TextContent(text="Explain the concept of machine learning in simple terms")]
    )
    
    request = AgenticRequest(
        message=message,
        session_id="test-session-2"
    )
    
    try:
        # Test invoke using the controller
        response = ChatController.chat(request)
        
        print(f"✅ Complex query response:")
        text_content = response.message.get_text_content()
        if text_content:
            print(f"   Message: {text_content.text[:200]}...")  # Truncate for readability
        else:
            print(f"   Message: No text content")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in complex query: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_server_endpoints():
    """Test the FastAPI server endpoints locally."""
    print("\n🧪 Testing server endpoints...")
    
    try:
        import httpx
        from agentic_platform.agent.langgraph_chat.server import app
        
        # Create test client
        async with httpx.AsyncClient(base_url="http://test") as client:
            client._transport = httpx.ASGITransport(app=app)
            
            # Test health endpoint
            health_response = await client.get("/health")
            print(f"✅ Health endpoint: {health_response.status_code} - {health_response.json()}")
            
            # Test chat endpoint
            test_request = {
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "Hello, what is 5 + 3?"}]
                },
                "session_id": "test-session-3"
            }
            
            chat_response = await client.post("/chat", json=test_request)
            print(f"✅ Chat endpoint: {chat_response.status_code}")
            if chat_response.status_code == 200:
                result = chat_response.json()
                print(f"   Response: {result['message']['content'][0]['text']}")
            else:
                print(f"   Error: {chat_response.text}")
            
            # Test invocations endpoint (alternative endpoint)
            invocations_response = await client.post("/invocations", json=test_request)
            print(f"✅ Invocations endpoint: {invocations_response.status_code}")
            if invocations_response.status_code == 200:
                result = invocations_response.json()
                print(f"   Response: {result['message']['content'][0]['text']}")
            
        return True
        
    except ImportError:
        print("❌ httpx not available for server testing. Install with: pip install httpx")
        return False
    except Exception as e:
        print(f"❌ Error in server testing: {e}")
        import traceback
        traceback.print_exc()
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
        "langgraph",
        "openai"
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
    litellm_key = os.getenv("LITELLM_KEY")
    litellm_endpoint = os.getenv("LITELLM_API_ENDPOINT")
    
    if litellm_key and litellm_endpoint:
        print(f"✅ LiteLLM configuration found")
        print(f"   Endpoint: {litellm_endpoint}")
        print(f"   Key: {litellm_key[:10]}...")
    else:
        print("⚠️  LiteLLM configuration not found")
        print("   Set LITELLM_KEY and LITELLM_API_ENDPOINT environment variables")
        print("   Example:")
        print('   export LITELLM_KEY="sk-05tIzUMzOi3rOSkrlocTfEXGktpvRRBFgnXTQl9QDIL1WjHX"')
        print('   export LITELLM_API_ENDPOINT="http://localhost:4000"')
    
    return True


def test_langgraph_workflow():
    """Test the LangGraph workflow directly."""
    print("\n🧪 Testing LangGraph workflow...")
    
    try:
        from agentic_platform.agent.langgraph_chat.chat_workflow import LangGraphChat
        from agentic_platform.agent.langgraph_chat.chat_prompt import ChatPrompt
        
        # Create workflow
        workflow = LangGraphChat()
        
        # Create test prompt
        inputs = {
            "chat_history": "",
            "message": "What is the capital of France?"
        }
        prompt = ChatPrompt(inputs=inputs)
        
        # Run workflow
        response = workflow.run(prompt)
        
        print(f"✅ LangGraph workflow response:")
        print(f"   Role: {response.role}")
        print(f"   Text: {response.text[:200]}...")  # Truncate for readability
        
        return True
        
    except Exception as e:
        print(f"❌ Error in LangGraph workflow: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🚀 Local LangGraph Chat Agent Testing")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        return
    
    # Check environment
    check_environment()
    
    # Run tests
    print("\n" + "=" * 50)
    print("Running Tests...")
    
    tests_passed = 0
    total_tests = 4
    
    # Test LangGraph workflow directly
    if test_langgraph_workflow():
        tests_passed += 1
    
    # Test basic invoke
    if await test_basic_invoke():
        tests_passed += 1
    
    # Test complex query
    if await test_complex_query():
        tests_passed += 1
    
    # Test server endpoints
    if await test_server_endpoints():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your langgraph_chat code is working locally.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n💡 Tips:")
        print("   - Make sure LiteLLM is running and accessible")
        print("   - Check that LITELLM_KEY and LITELLM_API_ENDPOINT are set")
        print("   - Ensure all dependencies are installed")


if __name__ == "__main__":
    asyncio.run(main())
