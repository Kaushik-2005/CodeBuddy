import re
from tools.tool_registry import ToolRegistry
from tools.file_tools import read_file, write_file, search_codebase, get_structure, delete_file, create_directory
from cli.interface import show_debug, show_success, show_error, show_info

class Agent:
    def __init__(self, llm_provider):
        self.llm = llm_provider
        self.tool_registry = ToolRegistry()
        self.debug_mode = False
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        self.tool_registry.register("read_file", read_file)
        self.tool_registry.register("write_file", write_file)
        self.tool_registry.register("search_codebase", search_codebase)
        self.tool_registry.register("get_structure", get_structure)
        self.tool_registry.register("delete_file", delete_file)
        self.tool_registry.register("create_directory", create_directory)
    
    def toggle_debug(self):
        """Toggle debug mode on/off"""
        self.debug_mode = not self.debug_mode
        status = "enabled" if self.debug_mode else "disabled"
        show_info(f"Debug mode {status}")
    
    def is_explanation_request(self, user_query: str) -> bool:
        """Check if the user is asking for an explanation rather than just file operations"""
        explanation_keywords = [
            'explain', 'understand', 'what does', 'how does', 'analyze', 
            'breakdown', 'describe', 'walk through', 'summarize', 'overview'
        ]
        return any(keyword in user_query.lower() for keyword in explanation_keywords)
    
    def select_tools(self, user_query: str) -> str:
        """Use LLM to determine which tools to use"""
        prompt = f"""
You are a coding assistant. A user asked: "{user_query}"

Available tools:
- read_file(filepath="path/to/file")
- write_file(filepath="path/to/file", content="file content here")
- search_codebase(search_term="search text", directory=".")
- get_structure(directory=".")
- delete_file(filepath="path/to/file")
- create_directory(directory_path="path/to/directory")

CRITICAL RULES:
1. ONLY respond with tool commands in the exact format: tool_name(param1="value1", param2="value2")
2. Do NOT include any explanatory text, comments, or code outside tool commands
3. When using write_file, put ALL code content in the content parameter with \\n for line breaks
4. Escape quotes inside content with \\\"

If multiple tools are needed, list them on separate lines.
Respond with ONLY tool commands:
"""
        
        return self.llm.ask(prompt)
    
    def explain_code(self, file_content: str, filepath: str, user_query: str) -> str:
        """Generate an explanation of the code"""
        prompt = f"""
You are a coding assistant. The user asked: "{user_query}"

Here is the code from {filepath}:

```
{file_content}
```

Please provide a clear, helpful explanation of this code. Include:
1. What the code does (main purpose)
2. Key components and how they work
3. Important functions/classes and their roles
4. Any notable patterns or techniques used
5. How different parts connect together

Make your explanation beginner-friendly but thorough.
"""
        
        return self.llm.ask(prompt)
    
    def parse_and_execute_tool(self, tool_command: str) -> str:
        """Parse tool command and execute it"""
        try:
            tool_command = tool_command.strip()
            
            if '"""' in tool_command:
                before_quotes = tool_command.split('"""')[0]
                content_part = tool_command.split('"""')[1]
                after_quotes = '"""'.join(tool_command.split('"""')[2:])
                escaped_content = content_part.replace('"', '\\"').replace('\n', '\\n')
                tool_command = before_quotes + '"' + escaped_content + '"' + after_quotes
            
            match = re.match(r'(\w+)\((.*)\)', tool_command)
            if not match:
                return f"Could not parse tool command: {tool_command}"
            
            tool_name = match.group(1)
            params_str = match.group(2)
            
            params = {}
            if params_str:
                if tool_name == "write_file" and 'content=' in params_str:
                    filepath_match = re.search(r'filepath="([^"]*)"', params_str)
                    if filepath_match:
                        params['filepath'] = filepath_match.group(1)
                    
                    content_match = re.search(r'content="(.*)"(?:\)|$)', params_str, re.DOTALL)
                    if content_match:
                        params['content'] = content_match.group(1)
                else:
                    current_param = ""
                    in_quotes = False
                    quote_char = None
                    param_parts = []
                    
                    for char in params_str:
                        if char in ['"', "'"] and not in_quotes:
                            in_quotes = True
                            quote_char = char
                            current_param += char
                        elif char == quote_char and in_quotes:
                            in_quotes = False
                            quote_char = None
                            current_param += char
                        elif char == ',' and not in_quotes:
                            param_parts.append(current_param.strip())
                            current_param = ""
                        else:
                            current_param += char
                    
                    if current_param:
                        param_parts.append(current_param.strip())
                    
                    for param in param_parts:
                        if '=' in param:
                            key, value = param.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            
                            params[key] = value
            
            result = self.tool_registry.execute(tool_name, **params)
            return result
            
        except Exception as e:
            return f"Error executing tool: {e}"
    
    def execute_command(self, user_query: str) -> str:
        """Main execution method"""
        # Check if this is an explanation request
        if self.is_explanation_request(user_query):
            # Try to extract filename from the query
            file_patterns = [
                r'(?:in|of|from)\s+([a-zA-Z0-9_./\\-]+\.(?:py|js|ts|java|cpp|c|md|txt|html|css))',
                r'([a-zA-Z0-9_./\\-]+\.(?:py|js|ts|java|cpp|c|md|txt|html|css))',
            ]
            
            filepath = None
            for pattern in file_patterns:
                match = re.search(pattern, user_query, re.IGNORECASE)
                if match:
                    filepath = match.group(1)
                    break
            
            if filepath:
                # Read the file and then explain it
                file_content = read_file(filepath)
                if not file_content.startswith("Error"):
                    explanation = self.explain_code(file_content, filepath, user_query)
                    return explanation
                else:
                    return file_content  # Return the error message
        
        # Regular tool execution for non-explanation requests
        tool_suggestion = self.select_tools(user_query)
        
        if self.debug_mode:
            show_debug(f"Tool suggestion: {tool_suggestion}")
        
        tool_lines = [line.strip() for line in tool_suggestion.split('\n') if line.strip()]
        
        results = []
        for tool_line in tool_lines:
            if not re.match(r'\w+\(.*\)', tool_line):
                if self.debug_mode:
                    show_debug(f"Skipping non-tool line: {tool_line}")
                continue
            
            if tool_line.startswith(('class ', 'def ', 'import ', 'from ', 'print(', '#')):
                if self.debug_mode:
                    show_debug(f"Skipping code line: {tool_line}")
                continue
            
            if self.debug_mode:
                show_debug(f"Executing: {tool_line}")
            
            result = self.parse_and_execute_tool(tool_line)
            
            if not any(keyword in result for keyword in ["Successfully", "Error", "Tool", "not found"]):
                results.append(result)
            else:
                if "Successfully" in result or "✅" in result:
                    show_success(result)
                elif "Error" in result or "not found" in result:
                    show_error(result)
        
        return '\n'.join(results)