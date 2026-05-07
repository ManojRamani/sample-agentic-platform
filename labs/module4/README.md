# Module 4: Advanced Agent Features

## Overview

This module explores advanced agent capabilities through Model Context Protocol (MCP) and multi-agent systems. You'll learn how to combine different agent frameworks, create specialized tool servers, and build interoperable AI systems that can collaborate effectively.

## Learning Objectives

- Create and deploy MCP-compatible tool servers
- Connect agents to multiple MCP servers simultaneously
- Mix and match different agent frameworks (PydanticAI, LangChain, etc.)
- Build collaborative multi-agent systems
- Integrate third-party MCP servers into your applications
- Interact with web applications using Amazon Bedrock AgentCore Browser Tool

## Prerequisites

- Completed Module 1 (Agentic Basics)
- Completed Module 2 (Workflow Agents)
- Completed Module 3 (Autonomous Agents)
- Python 3.10+
- AWS Bedrock access
- Basic understanding of async programming

## Installation

```bash
# Install dependencies from parent directory.
uv sync

# Navigate to module 4
cd labs/module4
```

## API Key Setup

This module requires API keys for external services. Create a `.env` file in the `labs/module4/notebooks/` directory:

```bash
cd notebooks
touch .env
```

Add the following API keys to your `.env` file:

```bash
# Tavily API Key (required for web search functionality)
TAVILY_KEY=your-tavily-key-here

# Nova Act API Key (required for browser automation with Amazon Bedrock AgentCore)
NOVA_ACT_API_KEY=your-nova-act-key-here
```

### Getting API Keys

1. **Tavily API Key**
   - Sign up at: <https://tavily.com>
   - Navigate to your dashboard to get your API key
   - Used in: Multi-agent delegation labs for web search capabilities

2. **Nova Act API Key**
   - Request access at: <https://nova.amazon.com/dev-apis>
   - Used in: Amazon Bedrock AgentCore browser tool labs
   - Enables automated browser interactions and web scraping

**Note:** The `.env` file is already in `.gitignore` to prevent accidentally committing your API keys.
