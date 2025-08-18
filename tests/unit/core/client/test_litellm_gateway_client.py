"""
Unit tests for LiteLLM Gateway Client.

This module contains unit tests for the LiteLLM Gateway Client,
testing the HTTP communication functionality with mocked responses.
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any

# Add the source directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../', 'src'))

from agentic_platform.core.client.llm_gateway.litellm_gateway_client import LiteLLMGatewayClient
from agentic_platform.core.models.llm_models import LLMRequest, LLMResponse, Usage
from agentic_platform.core.models.embedding_models import EmbedRequest, EmbedResponse
from agentic_platform.core.models.memory_models import Message, TextContent


class TestLiteLLMGatewayClient:
    """Unit tests for LiteLLM Gateway Client"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Store original environment variables
        self.original_endpoint = os.environ.get('LITELLM_API_ENDPOINT')
        self.original_key = os.environ.get('LITELLM_MASTER_KEY')
        
        # Clear environment variables to ensure clean state
        if 'LITELLM_API_ENDPOINT' in os.environ:
            del os.environ['LITELLM_API_ENDPOINT']
        if 'LITELLM_MASTER_KEY' in os.environ:
            del os.environ['LITELLM_MASTER_KEY']
        
        # Reload the module to pick up the cleared environment variables
        import importlib
        import agentic_platform.core.client.llm_gateway.litellm_gateway_client
        importlib.reload(agentic_platform.core.client.llm_gateway.litellm_gateway_client)
        from agentic_platform.core.client.llm_gateway.litellm_gateway_client import LiteLLMGatewayClient
        
        self.client = LiteLLMGatewayClient(api_key="test-key")
        
        # Sample request
        self.sample_request = LLMRequest(
            system_prompt="You are a helpful assistant.",
            messages=[
                Message(
                    role="user",
                    content=[TextContent(type="text", text="Hello, how are you?")]
                )
            ],
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            hyperparams={"temperature": 0.7, "max_tokens": 100}
        )
        
        # Sample LiteLLM response
        self.sample_litellm_response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! I'm doing well, thank you for asking. How can I help you today?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 15,
                "total_tokens": 25
            }
        }
    
    def teardown_method(self):
        """Clean up after tests"""
        # Restore original environment variables
        if self.original_endpoint is not None:
            os.environ['LITELLM_API_ENDPOINT'] = self.original_endpoint
        elif 'LITELLM_API_ENDPOINT' in os.environ:
            del os.environ['LITELLM_API_ENDPOINT']
            
        if self.original_key is not None:
            os.environ['LITELLM_MASTER_KEY'] = self.original_key
        elif 'LITELLM_MASTER_KEY' in os.environ:
            del os.environ['LITELLM_MASTER_KEY']
    
    def test_init_with_api_key(self):
        """Test client initialization with API key"""
        client = LiteLLMGatewayClient(api_key="custom-key")
        assert client.api_key == "custom-key"
        assert client.api_endpoint == "http://localhost:4000"
    
    def test_init_with_env_vars(self):
        """Test client initialization with environment variables"""
        with patch.dict('os.environ', {
            'LITELLM_API_ENDPOINT': 'http://custom-endpoint:8000',
            'LITELLM_MASTER_KEY': 'env-key'
        }):
            # Need to reload the module to pick up new env vars
            import importlib
            import agentic_platform.core.client.llm_gateway.litellm_gateway_client
            importlib.reload(agentic_platform.core.client.llm_gateway.litellm_gateway_client)
            from agentic_platform.core.client.llm_gateway.litellm_gateway_client import LiteLLMGatewayClient
            
            client = LiteLLMGatewayClient()
            assert client.api_key == "env-key"
            assert client.api_endpoint == "http://custom-endpoint:8000"
    
    def test_get_headers_with_api_key(self):
        """Test header generation with API key"""
        headers = self.client._get_headers()
        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-key"
        }
        assert headers == expected_headers
    
    def test_get_headers_with_auth_token(self):
        """Test header generation with auth token from context"""
        # Import the context module and set the token directly
        from agentic_platform.core.context.request_context import set_auth_token
        
        # Set the auth token in the context
        set_auth_token("context-token")
        
        try:
            # Create a new client instance to test the auth token logic
            client = LiteLLMGatewayClient(api_key="test-key")
            headers = client._get_headers()
            expected_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer context-token"
            }
            assert headers == expected_headers
        finally:
            # Clean up the context
            set_auth_token(None)
    
    @patch('agentic_platform.core.converter.litellm_converters.LiteLLMResponseConverter.to_llm_response')
    @patch('agentic_platform.core.converter.litellm_converters.LiteLLMRequestConverter.convert_llm_request')
    @patch('requests.post')
    def test_chat_invoke_success(self, mock_post, mock_convert_request, mock_convert_response):
        """Test successful chat completion request"""
        # Mock converter methods
        mock_convert_request.return_value = {"model": "test-model", "messages": []}
        mock_convert_response.return_value = LLMResponse(id="test-123", text="Test response")
        
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_litellm_response
        mock_post.return_value = mock_response
        
        # Make request
        response = self.client.chat_invoke(self.sample_request)
        
        # Verify HTTP request was made correctly
        mock_post.assert_called_once_with(
            "http://localhost:4000/v1/chat/completions",
            headers=self.client._get_headers(),
            json={"model": "test-model", "messages": []}
        )
        
        # Verify converters were called
        mock_convert_request.assert_called_once_with(self.sample_request)
        mock_convert_response.assert_called_once_with(self.sample_litellm_response)
        
        # Verify response
        assert isinstance(response, LLMResponse)
        assert response.id == "test-123"
    
    @patch('requests.post')
    def test_chat_invoke_http_error(self, mock_post):
        """Test chat completion request with HTTP error"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        # Make request and expect exception
        with pytest.raises(Exception) as exc_info:
            self.client.chat_invoke(self.sample_request)
        
        assert "LiteLLM API error: 400 - Bad Request" in str(exc_info.value)
    
    @patch('agentic_platform.core.converter.litellm_converters.LiteLLMResponseConverter.process_streaming_chunk')
    @patch('agentic_platform.core.converter.litellm_converters.LiteLLMResponseConverter.parse_streaming_line')
    @patch('agentic_platform.core.converter.litellm_converters.LiteLLMRequestConverter.convert_llm_request')
    @patch('requests.post')
    def test_chat_invoke_stream_success(self, mock_post, mock_convert_request, mock_parse_line, mock_process_chunk):
        """Test successful streaming chat completion request"""
        # Mock converter methods
        mock_convert_request.return_value = {"model": "test-model", "messages": []}
        mock_parse_line.side_effect = [
            {"id": "test-123", "choices": [{"delta": {"content": "Hello"}}]},
            {"id": "test-123", "choices": [{"delta": {"content": " world"}}]},
            {"done": True}
        ]
        mock_process_chunk.side_effect = [
            LLMResponse(id="test-123", text="Hello"),
            LLMResponse(id="test-123", text="Hello world", stop_reason="stop")
        ]
        
        # Mock streaming HTTP response
        streaming_data = [
            b'data: {"id":"test-123","choices":[{"delta":{"content":"Hello"}}]}',
            b'data: {"id":"test-123","choices":[{"delta":{"content":" world"}}]}',
            b'data: [DONE]'
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = streaming_data
        mock_post.return_value = mock_response
        
        # Make streaming request
        responses = list(self.client.chat_invoke_stream(self.sample_request))
        
        # Verify HTTP request was made with streaming enabled
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['stream'] is True
        assert call_args[1]['stream'] is True
        
        # Verify converters were called
        mock_convert_request.assert_called_once()
        assert mock_parse_line.call_count == 3  # All 3 lines are parsed, but [DONE] is filtered out
        assert mock_process_chunk.call_count == 2  # Only 2 valid chunks processed
        
        # Verify responses
        assert len(responses) == 2
        assert responses[0].text == "Hello"
        assert responses[1].text == "Hello world"
        assert responses[1].stop_reason == "stop"
    
    @patch('requests.post')
    def test_chat_invoke_stream_http_error(self, mock_post):
        """Test streaming request with HTTP error"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        # Make request and expect exception
        with pytest.raises(Exception) as exc_info:
            list(self.client.chat_invoke_stream(self.sample_request))
        
        assert "LiteLLM API error: 500 - Internal Server Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('agentic_platform.core.converter.litellm_converters.LiteLLMResponseConverter.process_streaming_chunk')
    @patch('agentic_platform.core.converter.litellm_converters.LiteLLMResponseConverter.parse_streaming_line')
    @patch('agentic_platform.core.converter.litellm_converters.LiteLLMRequestConverter.convert_llm_request')
    @patch('httpx.AsyncClient')
    async def test_chat_invoke_stream_async_success(self, mock_async_client, mock_convert_request, mock_parse_line, mock_process_chunk):
        """Test successful async streaming chat completion request"""
        # Mock converter methods
        mock_convert_request.return_value = {"model": "test-model", "messages": []}
        mock_parse_line.side_effect = [
            {"id": "test-123", "choices": [{"delta": {"content": "Hello"}}]},
            {"done": True}
        ]
        mock_process_chunk.return_value = LLMResponse(id="test-123", text="Hello", stop_reason="stop")
        
        # Mock async streaming response
        streaming_data = [
            'data: {"id":"test-123","choices":[{"delta":{"content":"Hello"}}]}',
            'data: [DONE]'
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        # Create async iterator for aiter_lines
        async def async_iter():
            for line in streaming_data:
                yield line
        
        mock_response.aiter_lines.return_value = async_iter()
        
        # Create proper async context manager
        class AsyncContextManager:
            async def __aenter__(self):
                return mock_response
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None
        
        mock_client_instance = Mock()
        mock_client_instance.stream.return_value = AsyncContextManager()
        
        # Create proper async context manager for the client
        class ClientAsyncContextManager:
            async def __aenter__(self):
                return mock_client_instance
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None
        
        mock_async_client.return_value = ClientAsyncContextManager()
        
        # Make async streaming request
        responses = []
        async for response in self.client.chat_invoke_stream_async(self.sample_request):
            responses.append(response)
        
        # Verify responses
        assert len(responses) == 1
        assert responses[0].text == "Hello"
        assert responses[0].stop_reason == "stop"
    
    @patch('requests.post')
    def test_embed_invoke_success(self, mock_post):
        """Test successful embedding request"""
        # Mock successful embedding response
        embedding_response = {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "index": 0
                }
            ],
            "model": "amazon.titan-embed-text-v2:0",
            "usage": {"prompt_tokens": 5, "total_tokens": 5}
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = embedding_response
        mock_post.return_value = mock_response
        
        # Create embedding request
        embed_request = EmbedRequest(
            text="Hello world",
            model_id="amazon.titan-embed-text-v2:0"
        )
        
        # Make request
        response = self.client.embed_invoke(embed_request)
        
        # Verify HTTP request was made correctly
        mock_post.assert_called_once_with(
            "http://localhost:4000/v1/embeddings",
            headers=self.client._get_headers(),
            json={
                "model": "amazon.titan-embed-text-v2:0",
                "input": "Hello world"
            }
        )
        
        # Verify response
        assert isinstance(response, EmbedResponse)
        assert response.embedding == [0.1, 0.2, 0.3, 0.4, 0.5]
    
    @patch('requests.post')
    def test_embed_invoke_http_error(self, mock_post):
        """Test embedding request with HTTP error"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        embed_request = EmbedRequest(
            text="Hello world",
            model_id="amazon.titan-embed-text-v2:0"
        )
        
        # Make request and expect exception
        with pytest.raises(Exception) as exc_info:
            self.client.embed_invoke(embed_request)
        
        assert "LiteLLM API error: 500 - Internal Server Error" in str(exc_info.value)
    
    def test_get_client(self):
        """Test get_client method"""
        client_info = self.client.get_client()
        
        assert isinstance(client_info, dict)
        assert "api_endpoint" in client_info
        assert "headers" in client_info
        assert client_info["api_endpoint"] == "http://localhost:4000"
        assert client_info["headers"]["Authorization"] == "Bearer test-key"
    
    def test_get_openai_client(self):
        """Test get_openai_client returns properly configured AsyncOpenAI client"""
        from openai import AsyncOpenAI
        
        openai_client = self.client.get_openai_client()
        
        # Verify it's an AsyncOpenAI instance
        assert isinstance(openai_client, AsyncOpenAI)
        
        # Verify the configuration (OpenAI client adds trailing slash)
        assert str(openai_client.base_url) == "http://localhost:4000/v1/"
        assert openai_client.api_key == "test-key"
