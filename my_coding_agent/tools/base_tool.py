"""
Base Tool Interface - Foundation for all agent tools
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Standardized tool result"""
    success: bool
    message: str
    data: Optional[Any] = None
    requires_approval: bool = False
    
    def __str__(self) -> str:
        return self.message


class BaseTool(ABC):
    """Abstract base class for all agent tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, str]:
        """Get tool parameter descriptions"""
        pass
    
    def validate_params(self, **kwargs) -> bool:
        """Validate parameters before execution"""
        required_params = self.get_parameters()
        for param in required_params:
            if param not in kwargs:
                return False
        return True


class ToolRegistry:
    """Registry for managing agent tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool"""
        self.tools[tool.name] = tool
        print(f"🔧 Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all tools"""
        return {name: tool.description for name, tool in self.tools.items()}
