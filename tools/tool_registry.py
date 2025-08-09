from typing import Dict, Callable, Any
import os

class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, function):
        """Register a tool function"""
        self.tools[name] = function
    
    def get_tool(self, name: str):
        """Get a registered tool function"""
        return self.tools.get(name)
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered"""
        return name in self.tools
    
    def list_tools(self) -> list:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def get_all_tools(self) -> dict:
        """Get all registered tools"""
        return self.tools.copy()