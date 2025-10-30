# My New Multi Agent Chat Agent

A comprehensive multi-agent system built on the Agentic Platform using the Strands framework. This agent demonstrates how to create a sophisticated multi-agent architecture with specialized agents for different types of tasks.

## Overview

This agent implements a multi-agent system with the following specialized agents:
- **Coordinator Agent**: Orchestrates interactions between specialized agents
- **Research Agent**: Handles information gathering and research tasks
- **Analysis Agent**: Performs mathematical calculations and analytical tasks
- **Creative Agent**: Manages creative writing and brainstorming tasks

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Agent Chat System                     │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Server (server.py)                                    │
│  ├── /health - Health check endpoint                           │
│  ├── /invoke - Synchronous chat endpoint                       │
│  ├── /invocations - Batch processing endpoint                  │
│  └── /stream - Streaming chat endpoint                         │
├─────────────────────────────────────────────────────────────────┤
│  Controller (controller/multi_agent_chat_controller.py)        │
│  ├── invoke() - Handle synchronous requests                    │
│  └── create_stream() - Handle streaming requests               │
├─────────────────────────────────────────────────────────────────┤
│  Multi-Agent System (agent/multi_agent_chat_agent.py)          │
│  ├── Coordinator Agent - Main orchestrator                     │
│  ├── Research Agent - Information gathering                    │
│  ├── Analysis Agent - Mathematical calculations                │
│  └── Creative Agent - Creative tasks                           │
├─────────────────────────────────────────────────────────────────┤
│  Tools & Utilities                                             │
│  ├── coordinate_agents - Agent coordination tool               │
│  ├── calculator - Mathematical calculations                    │
│  ├── StrandsStreamingConverter - Platform compatibility        │
│  └── System Prompts - Agent behavior definitions               │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
src/agentic_platform/agent/my_new_multi_agent_chat/
├── README.md                           # This documentation
├── Dockerfile                          # Container configuration
├── requirements.txt                    # Python dependencies
├── server.py                          # FastAPI server entry point
├── agent/
│   └── multi_agent_chat_agent.py      # Main multi-agent implementation
├── controller/
│   └── multi_agent_chat_controller.py # Request handling logic
├── prompt/
│   └── multi_agent_chat_prompt.py     # System prompts for agents
├── streaming/
│   └── strands_converter.py           # Streaming response converter
└── tool/
    └── collaboration_tool.py          # Agent coordination tools
```

## Key Components

### 1. Server (server.py)
FastAPI application with standard endpoints:
- `/health` - Health check (no authentication)
- `/invoke` - Synchronous chat interface (authenticated)
- `/invocations` - Batch processing (authenticated)
- `/stream` - Streaming chat interface (authenticated)

### 2. Multi-Agent System (agent/multi_agent_chat_agent.py)
Core implementation featuring:
- **Agent Strategy Determination**: Automatically selects appropriate agents based on query keywords
- **Specialized Agents**: Each agent has specific tools and system prompts
- **Coordination Logic**: Manages interactions between multiple agents
- **Streaming Support**: Full async streaming capability

### 3. Agent Coordination Tool (tool/collaboration_tool.py)
Custom tool for agent coordination:
```python
@tool
def coordinate_agents(task_description: str, agent_types: str) -> str:
    """Coordinate multiple agents for complex tasks."""
```

### 4. Streaming Converter (streaming/strands_converter.py)
Converts Strands framework events to platform-compatible StreamEvent types for real-time responses.

## Agent Strategy Logic

The system automatically determines which agents to use based on query keywords:

```python
def _determine_agent_strategy(self, query: str) -> str:
    query_lower = query.lower()
    
    research_keywords = ['research', 'find', 'search', 'information', 'facts', 'data']
    analysis_keywords = ['analyze', 'calculate', 'solve', 'problem', 'math', 'statistics']
    creative_keywords = ['create', 'write', 'story', 'creative', 'brainstorm', 'innovative']
    
    # Returns comma-separated list of needed agents
```

## Deployment Configuration

### Kubernetes Helm Values (k8s/helm/values/applications/my-new-multi-agent-chat-values.yaml)
```yaml
image:
  repository: "agentic-platform-my_new_multi_agent_chat"
  tag: latest

ingress:
  enabled: true
  path: "/multi-agent-chat"

service:
  type: ClusterIP
  port: 80
  targetPort: 8080
```

### Docker Configuration
Multi-stage build using UV package manager:
- Builder stage: Install dependencies
- Server stage: Copy source code and run application

## Integration Testing

Comprehensive EKS integration tests located in:
`tests/integ/workflows/my_new_multi_agent_chat/`

Tests cover:
- Infrastructure connectivity
- Service health and readiness
- Authentication flows
- Multi-agent functionality
- Streaming responses

## Usage Examples

### Mathematical Query (Analysis Agent)
```json
{
  "message": {
    "role": "user",
    "content": [{"type": "text", "text": "Calculate 15 * 8 and explain the process"}]
  },
  "session_id": "math-session"
}
```

### Creative Task (Creative Agent)
```json
{
  "message": {
    "role": "user", 
    "content": [{"type": "text", "text": "Write a short story about robots"}]
  },
  "session_id": "creative-session"
}
```

### Research Query (Research Agent)
```json
{
  "message": {
    "role": "user",
    "content": [{"type": "text", "text": "Research the benefits of renewable energy"}]
  },
  "session_id": "research-session"
}
```

## Response Format

All responses include metadata about the multi-agent system:

```json
{
  "message": {
    "role": "assistant",
    "content": [{"type": "text", "text": "Agent response..."}]
  },
  "session_id": "session-id",
  "metadata": {
    "agent_type": "strands_multi_agent_chat",
    "strategy_used": "analysis",
    "agents_available": ["coordinator", "research", "analysis", "creative"]
  }
}
```

## Development Notes

### Dependencies
- **Strands Framework**: Core agent implementation
- **FastAPI**: Web server framework
- **LiteLLM**: LLM proxy integration
- **Platform Core**: Shared models and utilities

### Authentication
Uses AWS Cognito M2M authentication for secured endpoints. Health endpoint remains public for monitoring.

### Streaming
Implements full async streaming using Server-Sent Events (SSE) with proper event conversion from Strands to platform format.

### Error Handling
Comprehensive error handling with proper HTTP status codes and detailed error messages.

## Extending the Agent

To add new specialized agents:

1. **Create Agent Instance**:
```python
self.new_agent = Agent(
    model=OpenAIModel(**self.model_config),
    tools=[relevant_tools],
    system_prompt="Agent-specific prompt"
)
```

2. **Update Strategy Logic**:
```python
new_keywords = ['keyword1', 'keyword2', 'keyword3']
if any(keyword in query_lower for keyword in new_keywords):
    agents_needed.append('new_agent')
```

3. **Add to Available Agents**:
Update metadata to include the new agent type.

## Performance Considerations

- **Resource Allocation**: 256Mi memory request, 512Mi limit
- **Scaling**: Horizontal pod autoscaling supported
- **Caching**: LLM responses cached at LiteLLM proxy level
- **Monitoring**: Comprehensive logging and health checks

---

This agent serves as a comprehensive example of building sophisticated multi-agent systems on the Agentic Platform, demonstrating best practices for agent coordination, streaming responses, and production deployment.
