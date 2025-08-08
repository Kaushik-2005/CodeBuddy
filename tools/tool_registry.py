from typing import Dict, Callable, Any
import os

class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, func: Callable):
        """Register a tool function"""
        self.tools[name] = func
    
    def execute(self, tool_name: str, **kwargs) -> str:
        """Execute a tool with given parameters"""
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"
        
        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            return f"Error executing {tool_name}: {e}"
    
    def list_tools(self) -> list:
        """Get list of available tools"""
        return list(self.tools.keys())