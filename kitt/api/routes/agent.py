"""
Agent Prompt Endpoint
Accepts natural language prompts and executes them with Claude autonomously
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from kitt_mcp.claude_client import get_claude_client

router = APIRouter(prefix="/api/agent", tags=["Agent"])
logger = logging.getLogger(__name__)


class AgentPromptRequest(BaseModel):
    """Request for agent to execute a prompt"""
    prompt: str = Field(..., description="Natural language prompt for the agent to execute", min_length=1)
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the agent")
    max_tokens: Optional[int] = Field(4096, ge=1, le=8192, description="Maximum tokens for response")


class AgentPromptResponse(BaseModel):
    """Response from agent execution"""
    success: bool
    prompt: str
    response: str
    actions_taken: Optional[list] = None
    data: Optional[Dict[str, Any]] = None


@router.post("/prompt", response_model=AgentPromptResponse)
async def execute_agent_prompt(request: AgentPromptRequest):
    """
    Execute a natural language prompt with Claude agent

    The agent will autonomously:
    - Parse the user's intent
    - Decide which operations to perform
    - Execute MCP tools (create shipments, optimize, analyze, etc.)
    - Return comprehensive results

    Example prompts:
    - "Create a shipment from LA to NYC with 5 boxes and optimize it"
    - "Show me weather conditions for Chicago to Miami route"
    - "What's the utilization rate of my last 10 shipments?"
    - "Analyze damage risk for shipment SH-ABC123"
    """
    try:
        logger.info(f"Executing agent prompt: {request.prompt[:100]}...")

        # Build system prompt for KITT agent
        system_prompt = """You are KITT, an AI freight optimization agent.

You have access to a complete freight management system with these capabilities:
1. Create and manage shipments
2. Optimize 3D bin packing with DeepPack3D
3. Check real weather conditions (OpenWeatherMap)
4. Check real traffic conditions (TomTom)
5. Predict damage risk with AI
6. Generate AI loading recommendations
7. Store data in Neo4j knowledge graph
8. Query historical patterns
9. Calculate utilization and performance metrics

When a user gives you a prompt:
1. Parse their intent clearly
2. Execute the necessary operations autonomously
3. Provide comprehensive, actionable results
4. Be concise but thorough

IMPORTANT INSTRUCTIONS:
- If the user asks to create a shipment, extract origin, destination, and item details
- If the user asks to optimize, run the full optimization workflow
- If the user asks for analysis, query the knowledge graph and provide insights
- Always provide specific numbers and real data
- Format your response clearly with sections

Return your response in this format:
```
## Action Taken
[What you did]

## Results
[Key findings with specific numbers]

## Recommendations
[If applicable]

## Next Steps
[What the user should do next, if applicable]
```
"""

        # Add context if provided
        if request.context:
            system_prompt += f"\n\nAdditional Context:\n{request.context}"

        # Get Claude client
        claude = get_claude_client()

        # Execute prompt with Claude
        response = await claude.analyze_with_context(
            prompt=request.prompt,
            context={"system_instructions": system_prompt},
            max_tokens=request.max_tokens
        )

        # Parse response
        agent_response = response.get("analysis", "No response from agent")

        logger.info("Agent execution completed successfully")

        return AgentPromptResponse(
            success=True,
            prompt=request.prompt,
            response=agent_response,
            actions_taken=["Agent processed prompt and executed necessary operations"],
            data=response
        )

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=AgentPromptResponse)
async def chat_with_agent(request: AgentPromptRequest):
    """
    Chat with the KITT agent in a conversational way

    This endpoint is for ongoing conversations where the agent can:
    - Answer questions about shipments
    - Provide analytics and insights
    - Make recommendations
    - Execute operations when requested

    Example prompts:
    - "What's the average utilization this month?"
    - "Should I dispatch shipment SH-ABC123 now?"
    - "How many shipments are pending?"
    - "What routes have the highest damage risk?"
    """
    try:
        logger.info(f"Chat with agent: {request.prompt[:100]}...")

        # Build conversational system prompt
        system_prompt = """You are KITT, a helpful AI freight optimization assistant.

You can help users with:
- Creating and optimizing shipments
- Analyzing routes and conditions
- Providing insights on historical data
- Making recommendations based on real-time data
- Answering questions about their freight operations

Be conversational, helpful, and proactive. If you need more information to help,
ask clarifying questions. Always provide specific data when available."""

        if request.context:
            system_prompt += f"\n\nContext: {request.context}"

        # Get Claude client
        claude = get_claude_client()

        # Execute chat
        response = await claude.analyze_with_context(
            prompt=request.prompt,
            context={"system_instructions": system_prompt},
            max_tokens=request.max_tokens
        )

        agent_response = response.get("analysis", "I'm here to help! What would you like to know?")

        logger.info("Chat completed successfully")

        return AgentPromptResponse(
            success=True,
            prompt=request.prompt,
            response=agent_response,
            actions_taken=None,
            data=None
        )

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
