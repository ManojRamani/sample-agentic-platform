"""Knowledge Base search tool for Strands."""

import os
import boto3
import logging
from strands import tool

logger = logging.getLogger(__name__)

# Initialize the client once at module level
knowledge_base_id = os.getenv('KNOWLEDGE_BASE_ID')

if not knowledge_base_id:
    logger.warning("KNOWLEDGE_BASE_ID environment variable not set. Knowledge base search will return mock data.")
    client = None
else:
    client = boto3.client('bedrock-agent-runtime')

@tool
def search_knowledge_base(query: str) -> str:
    """Search the Bedrock knowledge base for relevant information.
    
    Args:
        query: The search query to find relevant information
        
    Returns:
        Relevant information from the knowledge base
    """
    # If no knowledge base is configured, return mock data for testing
    if not client or not knowledge_base_id:
        logger.info(f"Mock knowledge base search for query: {query}")
        return f"Mock RAG response for query: '{query}'. This is a test response since no knowledge base is configured."
    
    try:
        response = client.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={'text': query},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5
                }
            }
        )
        
        results = []
        for result in response.get('retrievalResults', []):
            content = result.get('content', {}).get('text', '')
            if content:
                results.append(content)
        
        if results:
            return "\n\n".join(results)
        else:
            return "No relevant information found in the knowledge base."
            
    except Exception as e:
        logger.error(f"Error querying knowledge base: {e}")
        return f"Error accessing knowledge base: {str(e)}"
