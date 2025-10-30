"""Collaboration tool for multi-agent coordination."""

import logging
from strands import tool

logger = logging.getLogger(__name__)

@tool
def coordinate_agents(task_description: str, agent_types: str) -> str:
    """Coordinate between different specialized agents for complex tasks.
    
    Args:
        task_description: Description of the task that needs multi-agent coordination
        agent_types: Comma-separated list of agent types needed (e.g., "research,analysis,creative")
        
    Returns:
        Coordination strategy and simulated multi-agent response
    """
    try:
        # Parse agent types
        agents = [agent.strip() for agent in agent_types.split(',')]
        
        # Simulate coordination between agents
        coordination_response = f"Multi-Agent Coordination for: {task_description}\n\n"
        
        if 'research' in agents:
            coordination_response += "🔍 Research Agent: Gathering relevant information and data sources...\n"
            
        if 'analysis' in agents:
            coordination_response += "📊 Analysis Agent: Processing data and performing logical analysis...\n"
            
        if 'creative' in agents:
            coordination_response += "🎨 Creative Agent: Generating innovative ideas and creative solutions...\n"
            
        if 'coordinator' in agents:
            coordination_response += "🎯 Coordinator: Synthesizing inputs and providing comprehensive response...\n"
        
        coordination_response += f"\n✅ Coordination complete. {len(agents)} agent(s) collaborated on this task."
        
        logger.info(f"Coordinated agents: {agents} for task: {task_description}")
        
        return coordination_response
        
    except Exception as e:
        logger.error(f"Error in agent coordination: {e}")
        return f"Error coordinating agents: {str(e)}"
