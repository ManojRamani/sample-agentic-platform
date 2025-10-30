"""Multi-Agent Chat Agent implementation using Strands."""

import logging
from typing import AsyncGenerator

from strands import Agent
from strands_tools import calculator
from strands.models.openai import OpenAIModel

from agentic_platform.core.models.api_models import AgenticRequest, AgenticResponse
from agentic_platform.core.models.memory_models import Message, TextContent
from agentic_platform.core.models.streaming_models import StreamEvent
from agentic_platform.agent.my_new_multi_agent_chat.streaming.strands_converter import StrandsStreamingConverter
from agentic_platform.core.client.llm_gateway.llm_gateway_client import LLMGatewayClient, LiteLLMClientInfo
from agentic_platform.agent.my_new_multi_agent_chat.tool.collaboration_tool import coordinate_agents
from agentic_platform.agent.my_new_multi_agent_chat.prompt.multi_agent_chat_prompt import MULTI_AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class StrandsMultiAgentChatAgent:
    """Multi-Agent Chat implementation using Strands framework with multiple specialized agents."""

    def __init__(self):
        """Initialize the multi-agent system with specialized agents."""

        # Grab the proxy URL from our gateway client
        litellm_info: LiteLLMClientInfo = LLMGatewayClient.get_client_info()

        # Base model configuration for all agents
        self.model_config = {
            "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            "client_args": {
                "api_key": litellm_info.api_key,
                "base_url": litellm_info.api_endpoint,
                "timeout": 30
            }
        }

        # Initialize specialized agents
        self._init_specialized_agents()

        # Main coordinator agent
        self.coordinator = Agent(
            model=OpenAIModel(**self.model_config),
            tools=[coordinate_agents, calculator],
            system_prompt=MULTI_AGENT_SYSTEM_PROMPT
        )

    def _init_specialized_agents(self):
        """Initialize specialized agents for different tasks."""
        
        # Research Agent - specializes in information gathering
        self.research_agent = Agent(
            model=OpenAIModel(**self.model_config),
            tools=[],
            system_prompt="""You are a Research Agent specialized in gathering and analyzing information.
            Your role is to:
            1. Search for relevant information on given topics
            2. Analyze and synthesize findings
            3. Provide comprehensive research summaries
            4. Fact-check information and provide sources
            
            Always be thorough, accurate, and cite your sources when possible."""
        )

        # Analysis Agent - specializes in data analysis and problem solving
        self.analysis_agent = Agent(
            model=OpenAIModel(**self.model_config),
            tools=[calculator],
            system_prompt="""You are an Analysis Agent specialized in problem-solving and data analysis.
            Your role is to:
            1. Break down complex problems into manageable parts
            2. Perform calculations and mathematical analysis
            3. Identify patterns and trends in data
            4. Provide logical reasoning and conclusions
            
            Always show your work and explain your reasoning step by step."""
        )

        # Creative Agent - specializes in creative tasks
        self.creative_agent = Agent(
            model=OpenAIModel(**self.model_config),
            tools=[],
            system_prompt="""You are a Creative Agent specialized in creative and innovative thinking.
            Your role is to:
            1. Generate creative ideas and solutions
            2. Write engaging content and stories
            3. Brainstorm innovative approaches
            4. Think outside the box for unique perspectives
            
            Always be imaginative, original, and think creatively about problems."""
        )

    def _determine_agent_strategy(self, query: str) -> str:
        """Determine which agents should be involved based on the query."""
        query_lower = query.lower()
        
        # Keywords that suggest different agent types
        research_keywords = ['research', 'find', 'search', 'information', 'facts', 'data', 'study', 'investigate']
        analysis_keywords = ['analyze', 'calculate', 'solve', 'problem', 'math', 'statistics', 'logic', 'reasoning']
        creative_keywords = ['create', 'write', 'story', 'creative', 'brainstorm', 'innovative', 'design', 'imagine']
        
        agents_needed = []
        
        if any(keyword in query_lower for keyword in research_keywords):
            agents_needed.append('research')
        if any(keyword in query_lower for keyword in analysis_keywords):
            agents_needed.append('analysis')
        if any(keyword in query_lower for keyword in creative_keywords):
            agents_needed.append('creative')
            
        # If no specific keywords found, use coordinator for general queries
        if not agents_needed:
            agents_needed.append('coordinator')
            
        return ', '.join(agents_needed)

    def invoke(self, request: AgenticRequest) -> AgenticResponse:
        """Invoke the multi-agent system synchronously."""
        
        text_content = request.message.get_text_content()
        if text_content is None:
            raise ValueError("No text content found in request message")
        
        query = text_content.text
        
        # Determine which agents to use
        strategy = self._determine_agent_strategy(query)
        
        # For this example, we'll use the coordinator to orchestrate
        # In a more complex implementation, you could run multiple agents in parallel
        enhanced_query = f"[Multi-Agent Strategy: {strategy}] {query}"
        
        result = self.coordinator(enhanced_query)
        
        response_message = Message(
            role="assistant",
            content=[TextContent(text=str(result))]
        )
        
        return AgenticResponse(
            message=response_message,
            session_id=request.session_id or "default",
            metadata={
                "agent_type": "strands_multi_agent_chat",
                "strategy_used": strategy,
                "agents_available": ["coordinator", "research", "analysis", "creative"]
            }
        )

    async def invoke_stream(self, request: AgenticRequest) -> AsyncGenerator[StreamEvent, None]:
        """Invoke the multi-agent system with streaming support using async iterator."""        
        session_id = request.session_id or "default"
        converter = StrandsStreamingConverter(session_id)
        text_content = request.message.get_text_content()
        
        if text_content is None:
            from agentic_platform.core.models.streaming_models import ErrorEvent
            error_event = ErrorEvent(
                session_id=session_id,
                error="No text content found in request message"
            )
            yield error_event
            return
        
        try:
            query = text_content.text
            strategy = self._determine_agent_strategy(query)
            enhanced_query = f"[Multi-Agent Strategy: {strategy}] {query}"
            
            async for event in self.coordinator.stream_async(enhanced_query):
                # Convert Strands event to platform StreamEvents (can be multiple)
                platform_events = converter.convert_chunks_to_events(event)
                
                # Yield each event
                for platform_event in platform_events:
                    yield platform_event
                    
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            from agentic_platform.core.models.streaming_models import ErrorEvent
            error_event = ErrorEvent(
                session_id=session_id,
                error=str(e)
            )
            yield error_event
