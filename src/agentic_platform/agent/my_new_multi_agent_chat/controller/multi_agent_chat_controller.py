"""Controller for handling multi-agent chat requests."""

import logging
from typing import AsyncGenerator

from agentic_platform.core.models.api_models import AgenticRequest, AgenticResponse
from agentic_platform.core.models.streaming_models import StreamEvent
from agentic_platform.agent.my_new_multi_agent_chat.agent.multi_agent_chat_agent import StrandsMultiAgentChatAgent

logger = logging.getLogger(__name__)

# Module-level agent instance
agent = StrandsMultiAgentChatAgent()


async def invoke(request: AgenticRequest) -> AgenticResponse:
    """Invoke the agent with a standard response."""
    if request.stream:
        raise ValueError("Streaming requests should use the /stream endpoint")
    return agent.invoke(request)


async def create_stream(request: AgenticRequest) -> AsyncGenerator[StreamEvent, None]:
    """Create a streaming response for the agent."""
    async for stream_event in agent.invoke_stream(request):
        yield stream_event
