"""
Tier-2 router for tool selection

Analyzes user messages to determine which tool to use and with what parameters.
"""

from typing import Dict, Any, Optional
from .tool_registry import get_registry
import logging

logger = logging.getLogger(__name__)


class ToolRouter:
    """
    Router that analyzes user intent and selects appropriate tools.
    
    Uses LLM to analyze user messages and determine:
    - Which tool to use
    - What parameters to pass
    - Whether to use RAG or direct AI response
    """
    
    def __init__(self, gateway=None):
        """
        Initialize tool router.
        
        Args:
            gateway: AIGateway instance for LLM calls (optional, will be lazy-loaded)
        """
        self.gateway = gateway
        self.registry = get_registry()
    
    def _get_gateway(self):
        """Lazy load gateway if not provided."""
        if self.gateway is None:
            from llm.gateway import AIGateway
            self.gateway = AIGateway()
        return self.gateway
    
    async def route(
        self,
        message: str,
        available_tools: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Route user message to appropriate tool or direct response.
        
        Args:
            message: User message to route
            available_tools: List of available tool names (uses registry if None)
            
        Returns:
            Dictionary with routing decision:
            {
                "tool": "tool_name" or None,
                "parameters": {...},
                "use_rag": bool,
                "direct_response": bool
            }
        """
        # For now, return simple routing logic
        # TODO: Implement LLM-based intent analysis in future phase
        
        if available_tools is None:
            available_tools = self.registry.get_available_tools()
        
        # Simple heuristic: if message contains question words, use RAG
        question_words = ["what", "when", "where", "who", "why", "how", "which"]
        message_lower = message.lower()
        
        is_question = any(word in message_lower for word in question_words)
        
        # Default to RAG answer if it's available and looks like a question
        if "rag_answer" in available_tools and is_question:
            return {
                "tool": "rag_answer",
                "parameters": {"query": message, "top_k": 5},
                "use_rag": True,
                "direct_response": False
            }
        
        # Otherwise, direct AI response
        return {
            "tool": None,
            "parameters": {},
            "use_rag": False,
            "direct_response": True
        }
    
    def validate_tool_plan(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a tool execution plan.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        tool = self.registry.get_tool(tool_name)
        if tool is None:
            return False, f"Tool '{tool_name}' not found"
        
        if not self.registry.is_allowed(tool_name):
            return False, f"Tool '{tool_name}' is not in allowlist"
        
        is_valid, error_msg = tool.validate_parameters(parameters)
        return is_valid, error_msg
