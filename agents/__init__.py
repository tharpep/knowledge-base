"""
Agents package - Tool routing and execution

Provides:
- Base tool interface and abstract classes
- Tool registry for managing available tools
- Tool router for intent analysis and tool selection
- Tool implementations
"""

from .base_tool import BaseTool, ToolResult, ToolSchema
from .tool_registry import ToolRegistry, get_registry
from .router import ToolRouter

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolSchema",
    "ToolRegistry",
    "get_registry",
    "ToolRouter"
]
