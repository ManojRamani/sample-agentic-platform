# Module 5: Production Infrastructure for Agentic Systems

## Introduction

Module 5 focuses on building robust, production-ready agentic platforms with advanced infrastructure components. You'll learn how to implement telemetry, observability, and evaluation frameworks essential for running agents in production environments.

## Prerequisites

**⚠️ IMPORTANT:** The stack needs to be deployed in order to run Module 5 notebooks. Many notebooks in this module call APIs and use assets that live in the deployed AWS infrastructure stack. Please complete the infrastructure deployment steps before attempting to run these notebooks.

## Environment Setup

Before starting, make sure to:

1. Configure the Tavily API key in your `.env` file (instructions in `0_setup.ipynb`)
2. Ensure Docker is running for local services like Redis and PostgreSQL
3. Verify access to AWS services if running against the deployed stack

## Notebook Contents

### 0. Setup

- Configuring Tavily API for web search capabilities
- Environment configuration for local development
- Testing API connections

### 1. Observability and Telemetry (otel_telemetry)

- Implementing OpenTelemetry (OTEL) for tracing, metrics, and logging
- Creating facades to abstract telemetry providers
- Configuring exporters for telemetry data
- Building observability patterns for agentic systems

### 2. LLM Gateway

- Creating a centralized gateway for LLM requests
- Implementing rate limiting with Redis
- Building usage plans and request tracking
- Multi-tenant LLM request management

### 3. Agent Evaluation

- Building evaluation frameworks for agent performance
- Creating test cases and assertions
- Measuring success rates and efficiency metrics
- Using LLM judges for qualitative evaluation

### 4. Streaming

- Generating server sent events for streaming traces back.

## Working with the Deployed Stack

Many components in this module interact with deployed infrastructure:

- The Memory Gateway connects to PostgreSQL for storing session context and memories
- The LLM Gateway uses Redis for rate limiting and DynamoDB for usage tracking
- Telemetry components send data to OpenTelemetry collectors

## Troubleshooting

If you encounter issues:

1. Verify your local `.env` file is properly configured
2. Check that the infrastructure stack is deployed and accessible
3. For local development, ensure Docker containers are running
4. Confirm AWS credentials are properly configured for service access

## Next Steps

After completing this module, you'll have a solid understanding of the infrastructure components needed to run agentic systems at scale in production environments.
