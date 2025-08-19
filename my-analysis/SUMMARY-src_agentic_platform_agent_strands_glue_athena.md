# SUMMARY-src/agentic_platform/agent/strands_glue_athena.md

## Executive Summary

The Strands Glue/Athena agent is a specialized AI assistant that helps users discover and query data stored in AWS. It leverages Amazon Bedrock's Claude model through the Strands framework to provide a natural language interface for interacting with AWS Glue data catalogs and executing Athena queries. The agent allows users to search for tables, explore their structure, and run SQL queries against them without needing to write complex SQL or understand the underlying data architecture.

The implementation follows a clean architecture with separation of concerns between the API layer (server), controller logic, agent service, and specialized AWS tools. The agent is equipped with eight tools that enable it to search the Glue catalog, retrieve table details, list databases and tables, run Athena queries, generate SQL from natural language, and manage query executions.

## Implementation Details Breakdown

### Core Components

1. **Server Layer (`server.py`)**
   - Implements a FastAPI application with endpoints for chat, streaming chat, and health checks
   - Handles HTTP requests and delegates processing to the controller
   - Includes middleware for configuration and error handling

2. **Controller Layer (`agent_controller.py`)**
   - Abstracts the Strands-specific implementation from the rest of the system
   - Processes incoming requests and formats responses according to the platform's standard
   - Handles both synchronous and streaming interactions

3. **Service Layer (`agent_service.py`)**
   - Initializes and manages the Strands Agent with the Claude model
   - Configures the agent with the system prompt and available tools
   - Processes messages and handles streaming responses

4. **AWS Tools**
   - **Glue Tools (`glue_tools.py`)**: Functions for interacting with AWS Glue catalog
   - **Athena Tools (`athena_tools.py`)**: Functions for running and managing Athena queries

### Key Features

1. **Natural Language Table Search**
   - Uses fuzzy matching to find relevant tables based on names, columns, and descriptions
   - Scores and ranks results by relevance

2. **SQL Generation**
   - Converts natural language queries into SQL statements
   - Handles basic query patterns like "select all", "count", and filtered queries

3. **Query Execution and Results Retrieval**
   - Executes SQL queries against Athena
   - Manages asynchronous query execution with configurable wait times
   - Formats results into structured data for easy consumption

4. **Streaming Responses**
   - Supports streaming responses for better user experience
   - Converts Strands streaming format to the platform's standard event format

## Key Takeaways and Lessons Learned

1. **Separation of Concerns**
   - The codebase demonstrates clean separation between API handling, business logic, and AWS interactions
   - This makes the code more maintainable and testable

2. **Framework Abstraction**
   - The controller layer abstracts away Strands-specific details, allowing for potential future framework changes
   - Provides "2-way" compatibility between different frameworks

3. **Tool-based Architecture**
   - Breaking functionality into discrete tools allows the LLM to choose the appropriate action
   - Each tool has a clear purpose and well-defined inputs/outputs

4. **Error Handling**
   - Comprehensive error handling at multiple levels ensures robustness
   - Errors are captured, formatted, and returned in a user-friendly manner

5. **Streaming Support**
   - The implementation handles both synchronous and streaming interactions
   - Streaming provides a more responsive user experience for longer queries

## Technical Architecture Overview

```mermaid
    flowchart TD
        Client[Client] --> |HTTP Request| Server[FastAPI Server]
        Server --> |Delegates| Controller[Agent Controller]
        Controller --> |Processes Message| Service[Strands Glue/Athena Agent]
        Service --> |Uses| Claude[Claude 3 Sonnet Model]
        Service --> |Uses| Tools[AWS Tools]
        Tools --> |Interacts with| AWS[(AWS Services)]
        AWS --> |Glue Catalog| GlueDB[(AWS Glue)]
        AWS --> |Query Execution| Athena[(Amazon Athena)]
        AWS --> |Result Storage| S3[(Amazon S3)]
```

### Sequence Diagram for Query Flow

```mermaid
    sequenceDiagram
        participant User
        participant Server as FastAPI Server
        participant Controller as Agent Controller
        participant Agent as Strands Agent
        participant Claude as Claude 3 Model
        participant GlueTool as Glue Tools
        participant AthenaTool as Athena Tools
        participant AWS as AWS Services
    
        User->>Server: POST /chat with query
        Server->>Controller: Forward request
        Controller->>Agent: process_message()
        Agent->>Claude: Send user query with system prompt
        
        Claude->>GlueTool: search_glue_catalog()
        GlueTool->>AWS: Call Glue API
        AWS-->>GlueTool: Return matching tables
        GlueTool-->>Claude: Return search results
        
        Claude->>GlueTool: get_table_details()
        GlueTool->>AWS: Call Glue API
        AWS-->>GlueTool: Return table schema
        GlueTool-->>Claude: Return table details
        
        Claude->>AthenaTool: generate_sql_query()
        AthenaTool-->>Claude: Return SQL query
        
        Claude->>AthenaTool: run_athena_query()
        AthenaTool->>AWS: Execute query via Athena
        AWS-->>AthenaTool: Return query results
        AthenaTool-->>Claude: Return formatted results
        
        Claude-->>Agent: Generate response with results
        Agent-->>Controller: Return formatted response
        Controller-->>Server: Return API response
        Server-->>User: Return results to user
```

### Streaming Response Flow

```mermaid
    sequenceDiagram
        participant User
        participant Server as FastAPI Server
        participant Controller as Agent Controller
        participant Agent as Strands Agent
        participant Converter as Strands Streaming Converter
        participant Claude as Claude 3 Model
        participant Tools as AWS Tools
        participant AWS as AWS Services
    
        User->>Server: POST /chat/stream with query
        Server->>Controller: Forward request
        Controller->>Agent: stream_message()
        Agent->>Claude: Stream user query with system prompt
        
        loop For each chunk from Claude
            Claude-->>Agent: Return response chunk
            Agent->>Converter: Convert chunk to platform events
            Converter-->>Agent: Return standardized events
            Agent-->>Controller: Yield events
            Controller-->>Server: Stream events
            Server-->>User: Stream response chunks
    end
        
        Note over Claude,Tools: Tool calls happen during streaming
        Claude->>Tools: Call appropriate tool
        Tools->>AWS: Interact with AWS services
        AWS-->>Tools: Return results
        Tools-->>Claude: Return tool output
```

## Recommendations or Next Steps

1. **Enhanced Error Handling and Retries**
   - Implement more sophisticated retry mechanisms for AWS API calls
   - Add circuit breakers for improved resilience

2. **Performance Optimization**
   - Add caching for frequently accessed Glue catalog information
   - Implement pagination controls for large result sets

3. **Security Enhancements**
   - Add more granular IAM permissions for the agent role
   - Implement data access controls based on user identity

4. **User Experience Improvements**
   - Add support for query history and saved queries
   - Implement visualization capabilities for query results

5. **Advanced SQL Generation**
   - Enhance the SQL generation capability to handle more complex queries
   - Add support for joins, aggregations, and window functions

6. **Testing and Monitoring**
   - Add comprehensive unit and integration tests
   - Implement monitoring for query performance and error rates

7. **Multi-User Support**
   - Add user context to enable personalized experiences
   - Implement user-specific query history and preferences

8. **Documentation**
   - Create user documentation with example queries
   - Add developer documentation for extending the agent's capabilities

## Token Utilization Summary

- **Prompt Length**: 34690 characters
- **Estimated Token Count**: ~8672 tokens
- **Context Window Utilization**: ~4.3% of 200K token context window


---

*This summary was generated by Claude 3.7 Sonnet from Anthropic on 2025-08-18 at 13:41:48.*