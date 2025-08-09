import re
from tools.tool_registry import ToolRegistry
from tools.file_tools import read_file, write_file, search_codebase, get_structure, delete_file, create_directory, delete_directory, find_files, get_file_info
from tools.code_analysis_tools import validate_syntax, run_linter, find_references, analyze_complexity, code_quality_report
from memory.memory_manager import ConversationMemory
from cli.interface import show_debug, show_success, show_error, show_info

class Agent:
    def __init__(self, llm_provider):
        self.llm = llm_provider
        self.tool_registry = ToolRegistry()
        self.debug_mode = False
        self.memory = ConversationMemory()
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        # Filesystem tools
        self.tool_registry.register("read_file", read_file)
        self.tool_registry.register("find_files", find_files)  # New
        self.tool_registry.register("get_file_info", get_file_info)  # New
        self.tool_registry.register("write_file", write_file)
        self.tool_registry.register("search_codebase", search_codebase)
        self.tool_registry.register("get_structure", get_structure)
        self.tool_registry.register("delete_file", delete_file)
        self.tool_registry.register("create_directory", create_directory)
        self.tool_registry.register("delete_directory", delete_directory)
        
        # Code analysis tools
        self.tool_registry.register("validate_syntax", validate_syntax)
        self.tool_registry.register("run_linter", run_linter)
        self.tool_registry.register("find_references", find_references)
        self.tool_registry.register("analyze_complexity", analyze_complexity)
        self.tool_registry.register("code_quality_report", code_quality_report)
    
    def toggle_debug(self):
        """Toggle debug mode on/off"""
        self.debug_mode = not self.debug_mode
        status = "enabled" if self.debug_mode else "disabled"
        show_info(f"Debug mode {status}")
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear_memory()
        show_info("Memory cleared")
    
    def show_memory_stats(self):
        """Show current memory statistics"""
        stats = self.memory.get_memory_stats()
        show_info(f"Memory Stats: {stats['total_interactions']} interactions, {stats['total_files']} files")
        if stats['most_recent_file']:
            show_info(f"Last file: {stats['most_recent_file']}")
    
    def is_explanation_request(self, user_query: str) -> bool:
        """Check if the user is asking for an explanation"""
        explanation_keywords = [
            'explain', 'understand', 'what does', 'how does', 'analyze', 
            'breakdown', 'describe', 'walk through', 'summarize', 'overview'
        ]
        return any(keyword in user_query.lower() for keyword in explanation_keywords)
    
    def select_tools(self, user_query: str) -> str:
        """Use LLM to determine which tools to use"""
        context_info = self.memory.get_conversation_context()
        
        prompt = f"""
You are a coding assistant. A user asked: "{user_query}"

{context_info}

Available tools:
FILESYSTEM:
- read_file(filepath="path/to/file")
- write_file(filepath="path/to/file", content="file content here")
- search_codebase(search_term="search text", directory=".")
- get_structure(directory=".")
- delete_file(filepath="path/to/file")
- delete_directory(directory_path="path/to/directory")
- create_directory(directory_path="path/to/directory")

CODE ANALYSIS:
- validate_syntax(filepath="path/to/file")
- run_linter(filepath="path/to/file", linter_type="auto|pylint|flake8|eslint")
- find_references(symbol="function_name", directory=".", file_extensions=[".py", ".js"])
- analyze_complexity(filepath="path/to/file")
- code_quality_report(directory=".")

CONTEXT AWARENESS RULES:
- If user mentions "it", "this", or "the file", refer to recently worked files
- For code analysis requests, use appropriate analysis tools
- Pay attention to conversation history for context

CRITICAL RULES:
1. ONLY respond with tool commands: tool_name(param1="value1", param2="value2")
2. No explanatory text outside tool commands
3. Choose the right analysis tool based on user intent

Respond with ONLY tool commands:
"""
        
        return self.llm.ask(prompt)
    
    def explain_code(self, file_content: str, filepath: str, user_query: str) -> str:
        """Generate an explanation of the code"""
        context_info = self.memory.get_conversation_context()
        
        prompt = f"""
You are a coding assistant. The user asked: "{user_query}"

{context_info}

Here is the code from {filepath}:

```
{file_content}
```

Please provide a clear explanation of this code including:
1. Main purpose and functionality
2. Key components and how they work
3. Important functions/classes
4. Notable patterns or techniques

Make it beginner-friendly but thorough.
"""
        
        return self.llm.ask(prompt)
    
    def parse_and_execute_tool(self, tool_command: str) -> str:
        """Parse tool command and execute it"""
        try:
            tool_command = tool_command.strip()
            
            # Handle multi-line content
            if '"""' in tool_command:
                before_quotes = tool_command.split('"""')[0]
                content_part = tool_command.split('"""')[1]
                after_quotes = '"""'.join(tool_command.split('"""')[2:])
                escaped_content = content_part.replace('"', '\\"').replace('\n', '\\n')
                tool_command = before_quotes + '"' + escaped_content + '"' + after_quotes
            
            # Extract tool name and parameters
            match = re.match(r'(\w+)\((.*)\)', tool_command)
            if not match:
                return f"Could not parse tool command: {tool_command}"
            
            tool_name = match.group(1)
            params_str = match.group(2)
            
            # Parse parameters
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
                    # Regular parameter parsing
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
            
            # Execute the tool
            result = self.tool_registry.execute(tool_name, **params)
            return result
            
        except Exception as e:
            return f"Error executing tool: {e}"
    
    def execute_command(self, user_query: str) -> str:
        """Main execution method with memory integration"""
        files_involved = []
        
        # Handle special commands
        if user_query.lower() == "clear memory":
            self.clear_memory()
            return ""
        elif user_query.lower() == "memory stats":
            self.show_memory_stats()
            return ""
        
        # Check for explanation requests
        if self.is_explanation_request(user_query):
            # Try to find file reference
            filepath = self.memory.find_file_by_reference(user_query)
            
            if filepath:
                files_involved.append(filepath)
                file_content = read_file(filepath)
                if not file_content.startswith("Error"):
                    explanation = self.explain_code(file_content, filepath, user_query)
                    self.memory.add_interaction(user_query, explanation, files_involved)
                    return explanation
                else:
                    self.memory.add_interaction(user_query, file_content, files_involved)
                    return file_content
        
        # Regular tool execution
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
            
            # Track files involved
            if 'write_file' in tool_line:
                filepath_match = re.search(r'filepath="([^"]*)"', tool_line)
                if filepath_match:
                    files_involved.append(filepath_match.group(1))
            
            if not any(keyword in result for keyword in ["Successfully", "Error", "Tool", "not found"]):
                results.append(result)
            else:
                if "Successfully" in result or "✅" in result:
                    show_success(result)
                elif "Error" in result or "not found" in result:
                    show_error(result)
        
        # Add interaction to memory
        final_result = '\n'.join(results)
        self.memory.add_interaction(user_query, final_result, files_involved)
        
        return final_result