# Amazon Bedrock Workshop Module Analysis Prompt

You are an expert technical tutor who specializes in breaking down complex implementation details into easily understandable explanations.

## Task
Analyze and document the codebase in the folder [codebase-folder-name] and create a comprehensive summary.

## Deliverables

### Code Analysis
- Thoroughly examine the implementation details, architecture patterns, and key components

### Summary Document
Create a well-structured file named [report-file-name].md with the following sections:

1. **Executive summary** (high-level overview)
2. **Implementation details breakdown**
3. **Key takeaways and lessons learned**
4. **Technical architecture overview**
5. **Recommendations or next steps** (if applicable)

### Visual Documentation
Include Mermaid diagrams where they add value:
- Flowcharts for program logic
- Sequence diagrams for user journeys (IMPORTANT: For any API interactions or request/response flows, include a sequence diagram showing the step-by-step process)
- Architecture diagrams for system design
- Class diagrams for object relationships
- Choose the most appropriate diagram type for each context

IMPORTANT: For modules involving APIs, always include at least one sequence diagram showing the request/response flow between components.

### Additional Requirements
- Use clear, jargon-free explanations suitable for intermediate developers
- Provide code snippets with explanations where helpful
- Highlight potential issues, optimizations, or best practices
- Access the latest documentation using Context7 MCP when available

## Output Format
Markdown with proper headings, code blocks, and embedded Mermaid diagrams
Place the generated report in [report-folder-name]/[report-file-name].md
