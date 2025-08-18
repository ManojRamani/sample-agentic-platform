import pytest
import os
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import List

from agentic_platform.agent.pydanticai_agent.pyai_agent import PyAIAgent
from agentic_platform.core.models.api_models import AgenticRequest, AgenticResponse
from agentic_platform.core.models.memory_models import (
    Message, TextContent, SessionContext, ToolResult,
    UpsertSessionContextRequest, GetSessionContextRequest, GetSessionContextResponse
)


def mock_tool_function(query: str) -> str:
    """Mock tool function for testing"""
    return f"Mock result for: {query}"


@pytest.fixture
def mock_memory_client():
    """Mock the memory gateway client"""
    with patch('agentic_platform.agent.pydanticai_agent.pyai_agent.memory_client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_llm_gateway_client():
    """Mock the LLM gateway client"""
    with patch('agentic_platform.agent.pydanticai_agent.pyai_agent.LLMGatewayClient') as mock_client:
        # Mock the OpenAI client that would be returned
        mock_openai_client = Mock()
        mock_client.get_openai_client.return_value = mock_openai_client
        yield mock_client


@pytest.fixture
def mock_pydantic_ai_components():
    """Mock PydanticAI components"""
    with patch('agentic_platform.agent.pydanticai_agent.pyai_agent.Agent') as mock_agent_class, \
         patch('agentic_platform.agent.pydanticai_agent.pyai_agent.OpenAIModel') as mock_model, \
         patch('agentic_platform.agent.pydanticai_agent.pyai_agent.OpenAIProvider') as mock_provider:
        
        # Setup mock agent instance
        mock_agent_instance = Mock()
        mock_agent_instance.tool_plain = Mock()
        mock_agent_instance.run = AsyncMock()
        mock_agent_class.return_value = mock_agent_instance
        
        yield {
            'agent_class': mock_agent_class,
            'agent_instance': mock_agent_instance,
            'model': mock_model,
            'provider': mock_provider
        }


@pytest.fixture
def mock_converter():
    """Mock the PydanticAI message converter"""
    with patch('agentic_platform.agent.pydanticai_agent.pyai_agent.PydanticAIMessageConverter') as mock_conv:
        yield mock_conv


@pytest.fixture
def pyai_agent_with_mocks(mock_llm_gateway_client, mock_pydantic_ai_components):
    """Create PydanticAI agent with all dependencies mocked"""
    agent = PyAIAgent(tools=[mock_tool_function])
    return agent


class TestPyAIAgent:
    """Test PydanticAI Agent functionality with new agent types"""
    
    def test_agent_initialization(self, mock_llm_gateway_client, mock_pydantic_ai_components):
        """Test that PydanticAI agent initializes correctly"""
        # Create agent
        agent = PyAIAgent(tools=[mock_tool_function])
        
        # Verify initialization
        assert isinstance(agent.conversation, SessionContext)
        mock_llm_gateway_client.get_openai_client.assert_called_once()
        mock_pydantic_ai_components['provider'].assert_called_once()
        mock_pydantic_ai_components['model'].assert_called_once()
        mock_pydantic_ai_components['agent_class'].assert_called_once()
        mock_pydantic_ai_components['agent_instance'].tool_plain.assert_called_once_with(mock_tool_function)
    
    @pytest.mark.asyncio
    async def test_invoke_with_new_session(self, pyai_agent_with_mocks, mock_memory_client, 
                                         mock_pydantic_ai_components, mock_converter):
        """Test invoking agent with a new session"""
        # Setup mocks
        mock_memory_client.get_session_context.return_value = GetSessionContextResponse(results=[])
        
        # Mock PydanticAI response
        mock_model_response = Mock()
        mock_model_response.all_messages.return_value = []
        mock_pydantic_ai_components['agent_instance'].run.return_value = mock_model_response
        
        # Mock converter
        assistant_message = Message.from_text("assistant", "Hello! How can I help you?")
        mock_converter.convert_messages.return_value = [assistant_message]
        
        # Create request
        request = AgenticRequest.from_text("Hello", session_id="new-session-123")
        
        # Invoke agent
        response = await pyai_agent_with_mocks.invoke(request)
        
        # Verify response structure
        assert isinstance(response, AgenticResponse)
        assert response.session_id == "new-session-123"
        assert isinstance(response.message, Message)
        assert response.message.role == "assistant"
        assert response.text == "Hello! How can I help you?"
        assert "model" in response.metadata
    
    @pytest.mark.asyncio
    async def test_invoke_with_existing_session(self, pyai_agent_with_mocks, mock_memory_client,
                                              mock_pydantic_ai_components, mock_converter):
        """Test invoking agent with an existing session"""
        # Setup existing session
        existing_session = SessionContext(
            session_id="existing-session-456",
            messages=[Message.from_text("user", "Previous message")]
        )
        mock_memory_client.get_session_context.return_value = GetSessionContextResponse(
            results=[existing_session]
        )
        
        # Mock PydanticAI response
        mock_model_response = Mock()
        mock_model_response.all_messages.return_value = []
        mock_pydantic_ai_components['agent_instance'].run.return_value = mock_model_response
        
        # Mock converter
        assistant_message = Message.from_text("assistant", "I remember our previous conversation.")
        mock_converter.convert_messages.return_value = [assistant_message]
        
        # Create request
        request = AgenticRequest.from_text("Continue our chat", session_id="existing-session-456")
        
        # Invoke agent
        response = await pyai_agent_with_mocks.invoke(request)
        
        # Verify session was loaded
        mock_memory_client.get_session_context.assert_called_once()
        assert response.session_id == "existing-session-456"
        assert response.text == "I remember our previous conversation."
    
    @pytest.mark.asyncio
    async def test_invoke_with_multi_turn_messages(self, pyai_agent_with_mocks, mock_memory_client,
                                                 mock_pydantic_ai_components, mock_converter):
        """Test agent with multi-turn conversation in request"""
        # Setup mocks
        mock_memory_client.get_session_context.return_value = GetSessionContextResponse(results=[])
        
        # Mock PydanticAI response
        mock_model_response = Mock()
        mock_model_response.all_messages.return_value = []
        mock_pydantic_ai_components['agent_instance'].run.return_value = mock_model_response
        
        # Mock converter
        assistant_message = Message.from_text("assistant", "I understand the context from our conversation.")
        mock_converter.convert_messages.return_value = [assistant_message]
        
        # Create request with latest user message
        latest_message = Message.from_text("user", "Actually, what about tomorrow?")
        request = AgenticRequest(message=latest_message, session_id="multi-turn-session")
        
        # Invoke agent
        response = await pyai_agent_with_mocks.invoke(request)
        
        # Verify user text was used for PydanticAI
        mock_pydantic_ai_components['agent_instance'].run.assert_called_once_with("Actually, what about tomorrow?")
        assert response.session_id == "multi-turn-session"
        assert response.text == "I understand the context from our conversation."
    
    @pytest.mark.asyncio
    async def test_invoke_saves_conversation(self, pyai_agent_with_mocks, mock_memory_client,
                                           mock_pydantic_ai_components, mock_converter):
        """Test that conversation is saved after agent invocation"""
        # Setup mocks
        mock_memory_client.get_session_context.return_value = GetSessionContextResponse(results=[])
        
        # Mock PydanticAI response
        mock_model_response = Mock()
        mock_model_response.all_messages.return_value = []
        mock_pydantic_ai_components['agent_instance'].run.return_value = mock_model_response
        
        # Mock converter
        assistant_message = Message.from_text("assistant", "Response saved to memory.")
        mock_converter.convert_messages.return_value = [assistant_message]
        
        # Create request
        request = AgenticRequest.from_text("Save this conversation", session_id="save-session")
        
        # Invoke agent
        response = await pyai_agent_with_mocks.invoke(request)
        
        # Verify conversation was saved
        mock_memory_client.upsert_session_context.assert_called_once()
        call_args = mock_memory_client.upsert_session_context.call_args[0][0]
        assert isinstance(call_args, UpsertSessionContextRequest)
        assert call_args.session_context.session_id == "save-session"
    
    @pytest.mark.asyncio
    async def test_invoke_with_multiple_assistant_messages(self, pyai_agent_with_mocks, mock_memory_client,
                                                         mock_pydantic_ai_components, mock_converter):
        """Test agent handling multiple assistant messages from PydanticAI"""
        # Setup mocks
        mock_memory_client.get_session_context.return_value = GetSessionContextResponse(results=[])
        
        # Mock PydanticAI response
        mock_model_response = Mock()
        mock_model_response.all_messages.return_value = []
        mock_pydantic_ai_components['agent_instance'].run.return_value = mock_model_response
        
        # Mock converter with multiple assistant messages
        assistant_messages = [
            Message.from_text("assistant", "Let me think about this..."),
            Message.from_text("assistant", "Here's my final answer: The solution is X.")
        ]
        mock_converter.convert_messages.return_value = assistant_messages
        
        # Create request
        request = AgenticRequest.from_text("Complex question", session_id="complex-session")
        
        # Invoke agent
        response = await pyai_agent_with_mocks.invoke(request)
        
        # Verify last assistant message is returned
        assert response.text == "Here's my final answer: The solution is X."
        assert response.session_id == "complex-session"
    
    @pytest.mark.asyncio
    async def test_invoke_handles_no_user_message(self, pyai_agent_with_mocks, mock_memory_client):
        """Test agent raises error when no user message is found"""
        # Setup mocks
        mock_memory_client.get_session_context.return_value = GetSessionContextResponse(results=[])
        
        # Create request with only assistant message
        assistant_message = Message.from_text("assistant", "Only assistant message")
        request = AgenticRequest(message=assistant_message, session_id="no-user-session")
        
        # Invoke agent and expect error
        with pytest.raises(ValueError, match="No user message found in request"):
            await pyai_agent_with_mocks.invoke(request)
    
    @pytest.mark.asyncio
    async def test_invoke_handles_no_assistant_messages(self, pyai_agent_with_mocks, mock_memory_client,
                                                      mock_pydantic_ai_components, mock_converter):
        """Test agent fallback when no assistant messages are returned"""
        # Setup mocks
        mock_memory_client.get_session_context.return_value = GetSessionContextResponse(results=[])
        
        # Mock PydanticAI response
        mock_model_response = Mock()
        mock_model_response.all_messages.return_value = []
        mock_pydantic_ai_components['agent_instance'].run.return_value = mock_model_response
        
        # Mock converter returning no assistant messages
        mock_converter.convert_messages.return_value = []
        
        # Create request
        request = AgenticRequest.from_text("No assistant response test")
        
        # Invoke agent
        response = await pyai_agent_with_mocks.invoke(request)
        
        # Verify fallback message
        assert response.message.role == "assistant"
        assert response.text == "No response generated"
    
    @pytest.mark.asyncio
    async def test_invoke_creates_session_when_none_exists(self, pyai_agent_with_mocks, mock_memory_client,
                                                         mock_pydantic_ai_components, mock_converter):
        """Test agent creates new session when existing session is not found"""
        # Setup mocks - simulate session not found
        mock_memory_client.get_session_context.return_value = GetSessionContextResponse(results=[])
        
        # Mock PydanticAI response
        mock_model_response = Mock()
        mock_model_response.all_messages.return_value = []
        mock_pydantic_ai_components['agent_instance'].run.return_value = mock_model_response
        
        # Mock converter
        assistant_message = Message.from_text("assistant", "New session created.")
        mock_converter.convert_messages.return_value = [assistant_message]
        
        # Create request with session ID
        request = AgenticRequest.from_text("Create new session", session_id="new-session-789")
        
        # Invoke agent
        response = await pyai_agent_with_mocks.invoke(request)
        
        # Verify new session was created
        assert response.session_id == "new-session-789"
        assert response.text == "New session created."
    
    @pytest.mark.asyncio
    async def test_invoke_without_session_id(self, pyai_agent_with_mocks, mock_memory_client,
                                           mock_pydantic_ai_components, mock_converter):
        """Test agent creates session when no session ID provided"""
        # Setup mocks
        mock_memory_client.get_session_context.return_value = GetSessionContextResponse(results=[])
        
        # Mock PydanticAI response
        mock_model_response = Mock()
        mock_model_response.all_messages.return_value = []
        mock_pydantic_ai_components['agent_instance'].run.return_value = mock_model_response
        
        # Mock converter
        assistant_message = Message.from_text("assistant", "Session auto-created.")
        mock_converter.convert_messages.return_value = [assistant_message]
        
        # Create request without session ID
        request = AgenticRequest.from_text("No session ID")
        
        # Invoke agent
        response = await pyai_agent_with_mocks.invoke(request)
        
        # Verify session was created (session_id will be auto-generated)
        assert response.session_id is not None
        assert len(response.session_id) > 0
        assert response.text == "Session auto-created."
