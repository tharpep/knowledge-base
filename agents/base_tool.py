"""
Base tool interface and abstract class

All tools must inherit from BaseTool and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """Standard tool execution result."""
    success: bool = Field(..., description="Whether the tool execution was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Tool output data")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time_ms: Optional[float] = Field(None, description="Tool execution time in milliseconds")
    citations: Optional[list[str]] = Field(default_factory=list, description="Source citations if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"answer": "Example response"},
                "error": None,
                "execution_time_ms": 123.45,
                "citations": ["doc1", "doc2"]
            }
        }


class ToolSchema(BaseModel):
    """Tool schema definition for validation and documentation."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameter schema (JSON Schema format)")
    returns: Dict[str, Any] = Field(..., description="Tool return schema (JSON Schema format)")
    read_only: bool = Field(True, description="Whether tool is read-only (no side effects)")
    idempotent: bool = Field(True, description="Whether tool is idempotent")


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    All tools must inherit from this class and implement:
    - name: Tool identifier
    - description: Human-readable description
    - execute(): Tool execution logic
    - get_schema(): Tool schema for validation
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool identifier (e.g., 'rag_answer', 'web_search')."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable tool description."""
        pass
    
    @property
    def read_only(self) -> bool:
        """Whether tool is read-only (default: True)."""
        return True
    
    @property
    def idempotent(self) -> bool:
        """Whether tool is idempotent (default: True)."""
        return True
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with execution outcome
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> ToolSchema:
        """
        Get tool schema for validation and documentation.
        
        Returns:
            ToolSchema with parameter and return definitions
        """
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate tool parameters against schema.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        schema = self.get_schema()
        required_params = schema.parameters.get("required", [])
        properties = schema.parameters.get("properties", {})
        
        # Check required parameters
        for param in required_params:
            if param not in parameters:
                return False, f"Missing required parameter: {param}"
        
        # Validate parameter types (basic validation)
        for param_name, param_value in parameters.items():
            if param_name in properties:
                param_schema = properties[param_name]
                expected_type = param_schema.get("type")
                
                if expected_type == "string" and not isinstance(param_value, str):
                    return False, f"Parameter '{param_name}' must be a string"
                elif expected_type == "integer" and not isinstance(param_value, int):
                    return False, f"Parameter '{param_name}' must be an integer"
                elif expected_type == "number" and not isinstance(param_value, (int, float)):
                    return False, f"Parameter '{param_name}' must be a number"
                elif expected_type == "boolean" and not isinstance(param_value, bool):
                    return False, f"Parameter '{param_name}' must be a boolean"
        
        return True, None

