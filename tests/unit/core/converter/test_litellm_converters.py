"""
Unit tests for LiteLLM Converters.

This module contains unit tests for the LiteLLM request and response converters,
testing the conversion logic between internal types and LiteLLM API format.
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock

# Add the source directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../', 'src'))

from agentic_platform.core.converter.litellm_converters import LiteLLMRequestConverter, LiteLLMResponseConverter
from agentic_platform.core.models.llm_models import LLMRequest, LLMResponse, Usage
from agentic_platform.core.models.memory_models import Message, ToolCall, TextContent
from agentic_platform.core.models.tool_models import ToolSpec
from pydantic import BaseModel


class WeatherParams(BaseModel):
    """Test tool parameters"""
    location: str
    unit: str = "celsius"


class TestLiteLLMRequestConverter:
    """Unit tests for LiteLLM Request Converter"""
    
    def test_convert_message_text_only(self):
        """Test converting a simple text message"""
        message = Message(
            role="user",
            content=[TextContent(type="text", text="Hello, how are you?")]
        )
        
        result = LiteLLMRequestConverter.convert_message(message)
        
        expected = {
            "role": "user",
            "content": "Hello, how are you?"
        }
        assert result == expected
    
    def test_convert_message_with_tool_calls(self):
        """Test converting a message with tool calls"""
        message = Message(
            role="assistant",
            content=[TextContent(type="text", text="I'll check the weather for you.")],
            tool_calls=[
                ToolCall(
                    id="call_123",
                    name="get_weather",
                    arguments={"location": "New York", "unit": "celsius"}
                )
            ]
        )
        
        result = LiteLLMRequestConverter.convert_message(message)
        
        expected = {
            "role": "assistant",
            "content": "I'll check the weather for you.",
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"location": "New York", "unit": "celsius"}'
                    }
                }
            ]
        }
        assert result == expected
    
    def test_convert_messages_list(self):
        """Test converting a list of messages"""
        messages = [
            Message(
                role="user",
                content=[TextContent(type="text", text="Hello")]
            ),
            Message(
                role="assistant",
                content=[TextContent(type="text", text="Hi there!")]
            )
        ]
        
        result = LiteLLMRequestConverter.convert_messages(messages)
        
        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        assert result == expected
    
    def test_convert_tools(self):
        """Test converting tool specifications"""
        # Create a mock tool spec
        tool_spec = Mock()
        tool_spec.name = "get_weather"
        tool_spec.description = "Get weather information"
        tool_spec.model.model_json_schema.return_value = {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
        
        result = LiteLLMRequestConverter.convert_tools([tool_spec])
        
        expected = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        assert result == expected
    
    def test_convert_llm_request_basic(self):
        """Test converting a basic LLM request"""
        request = LLMRequest(
            system_prompt="You are a helpful assistant.",
            messages=[
                Message(
                    role="user",
                    content=[TextContent(type="text", text="Hello")]
                )
            ],
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            hyperparams={"temperature": 0.7, "max_tokens": 100}
        )
        
        result = LiteLLMRequestConverter.convert_llm_request(request)
        
        expected = {
            "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        assert result == expected
    
    def test_convert_llm_request_with_tools(self):
        """Test converting an LLM request with tools"""
        # Create a real tool spec instead of mock
        class TestToolParams(BaseModel):
            location: str
        
        tool_spec = ToolSpec(
            name="get_weather",
            description="Get weather information",
            model=TestToolParams
        )
        
        request = LLMRequest(
            system_prompt="You are a helpful assistant.",
            messages=[
                Message(
                    role="user",
                    content=[TextContent(type="text", text="What's the weather?")]
                )
            ],
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            hyperparams={"temperature": 0.7},
            tools=[tool_spec],
            force_tool="get_weather"
        )
        
        result = LiteLLMRequestConverter.convert_llm_request(request)
        
        assert "tools" in result
        assert len(result["tools"]) == 1
        assert result["tools"][0]["type"] == "function"
        assert result["tools"][0]["function"]["name"] == "get_weather"
        assert result["tools"][0]["function"]["description"] == "Get weather information"
        assert result["tool_choice"] == {
            "type": "function",
            "function": {"name": "get_weather"}
        }


class TestLiteLLMResponseConverter:
    """Unit tests for LiteLLM Response Converter"""
    
    def test_to_llm_response_basic(self):
        """Test converting a basic LiteLLM response"""
        litellm_response = {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 8,
                "total_tokens": 18
            }
        }
        
        result = LiteLLMResponseConverter.to_llm_response(litellm_response)
        
        assert isinstance(result, LLMResponse)
        assert result.id == "chatcmpl-123"
        assert result.text == "Hello! How can I help you?"
        assert result.stop_reason == "stop"
        assert result.usage.prompt_tokens == 10
        assert result.usage.completion_tokens == 8
        assert result.usage.total_tokens == 18
        assert len(result.output) == 1
        assert result.output[0].role == "assistant"
    
    def test_to_llm_response_with_tool_calls(self):
        """Test converting a LiteLLM response with tool calls"""
        litellm_response = {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "",  # Empty string instead of None
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "New York"}'
                                }
                            }
                        ]
                    },
                    "finish_reason": "tool_calls"
                }
            ],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 5,
                "total_tokens": 25
            }
        }
        
        result = LiteLLMResponseConverter.to_llm_response(litellm_response)
        
        assert isinstance(result, LLMResponse)
        assert result.id == "chatcmpl-123"
        assert result.text == ""  # Empty string when tool calls are present
        assert result.stop_reason == "tool_calls"
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].id == "call_123"
        assert result.tool_calls[0].name == "get_weather"
        assert result.tool_calls[0].arguments == {"location": "New York"}
    
    def test_to_llm_response_empty_choices(self):
        """Test converting a LiteLLM response with no choices"""
        litellm_response = {
            "id": "chatcmpl-123",
            "choices": []
        }
        
        result = LiteLLMResponseConverter.to_llm_response(litellm_response)
        
        assert isinstance(result, LLMResponse)
        assert result.raw_response == litellm_response
    
    def test_parse_streaming_line_valid_data(self):
        """Test parsing a valid streaming line"""
        line = 'data: {"id": "chatcmpl-123", "choices": [{"delta": {"content": "Hello"}}]}'
        
        result = LiteLLMResponseConverter.parse_streaming_line(line)
        
        expected = {
            "id": "chatcmpl-123",
            "choices": [{"delta": {"content": "Hello"}}]
        }
        assert result == expected
    
    def test_parse_streaming_line_done_marker(self):
        """Test parsing the [DONE] marker"""
        line = 'data: [DONE]'
        
        result = LiteLLMResponseConverter.parse_streaming_line(line)
        
        assert result == {"done": True}
    
    def test_parse_streaming_line_invalid_json(self):
        """Test parsing a line with invalid JSON"""
        line = 'data: {invalid json}'
        
        result = LiteLLMResponseConverter.parse_streaming_line(line)
        
        assert result == {}
    
    def test_parse_streaming_line_no_data_prefix(self):
        """Test parsing a line without data prefix"""
        line = 'some other line'
        
        result = LiteLLMResponseConverter.parse_streaming_line(line)
        
        assert result == {}
    
    def test_process_streaming_chunk_text_content(self):
        """Test processing a streaming chunk with text content"""
        chunk_data = {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "delta": {"content": "Hello"},
                    "index": 0
                }
            ]
        }
        accumulated_state = {}
        
        result = LiteLLMResponseConverter.process_streaming_chunk(chunk_data, accumulated_state)
        
        assert isinstance(result, LLMResponse)
        assert result.id == "chatcmpl-123"
        assert result.text == "Hello"
        assert accumulated_state["accumulated_text"] == "Hello"
        assert result.stop_reason is None
    
    def test_process_streaming_chunk_accumulate_text(self):
        """Test processing multiple streaming chunks that accumulate text"""
        accumulated_state = {"accumulated_text": "Hello", "accumulated_tool_calls": []}
        
        chunk_data = {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "delta": {"content": " world"},
                    "index": 0
                }
            ]
        }
        
        result = LiteLLMResponseConverter.process_streaming_chunk(chunk_data, accumulated_state)
        
        assert result.text == "Hello world"
        assert accumulated_state["accumulated_text"] == "Hello world"
    
    def test_process_streaming_chunk_with_finish_reason(self):
        """Test processing a streaming chunk with finish reason and usage"""
        chunk_data = {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "delta": {},
                    "finish_reason": "stop",
                    "index": 0
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        accumulated_state = {"accumulated_text": "Hello world", "accumulated_tool_calls": []}
        
        result = LiteLLMResponseConverter.process_streaming_chunk(chunk_data, accumulated_state)
        
        assert result.stop_reason == "stop"
        assert result.usage.prompt_tokens == 10
        assert result.usage.completion_tokens == 5
        assert result.usage.total_tokens == 15
    
    def test_process_streaming_chunk_tool_calls(self):
        """Test processing a streaming chunk with tool calls"""
        chunk_data = {
            "id": "chatcmpl-123",
            "choices": [
                {
                    "delta": {
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": "call_123",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "Paris"}'
                                }
                            }
                        ]
                    },
                    "index": 0
                }
            ]
        }
        accumulated_state = {}
        
        result = LiteLLMResponseConverter.process_streaming_chunk(chunk_data, accumulated_state)
        
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].id == "call_123"
        assert result.tool_calls[0].name == "get_weather"
        assert result.tool_calls[0].arguments == {"location": "Paris"}
        assert len(accumulated_state["accumulated_tool_calls"]) == 1
