import re
from tools.tool_registry import ToolRegistry
from tools.file_tools import read_file, write_file, search_codebase, get_structure, delete_file, create_directory, delete_directory, find_files, get_file_info
from tools.code_analysis_tools import validate_syntax, run_linter, find_references, analyze_complexity, code_quality_report
from tools.execution_tools import run_python, run_tests, run_command, install_package, check_environment
from memory.memory_manager import ConversationMemory
from memory.enhanced_memory import EnhancedMemory
from agent.prompt_manager import PromptManager
from agent.react_agent import ReActAgent
from cli.interface import show_debug, show_success, show_error, show_info
from workflows.codebase_analysis import CodebaseAnalysisWorkflow

class Agent:
    def __init__(self, llm_provider):
        self.llm = llm_provider
        self.tool_registry = ToolRegistry()
        self.debug_mode = False
        
        # Enhanced memory system
        self.enhanced_memory = EnhancedMemory()
        
        # Legacy memory for compatibility
        self.memory = ConversationMemory()
        self.prompt_manager = PromptManager(self.memory)
        self._register_tools()
        
        # ReAct agent with proper integration
        self.react_agent = ReActAgent(llm_provider, self.tool_registry, self.enhanced_memory, agent_instance=self)
    
    def _register_tools(self):
        """Register all available tools"""
        # Filesystem tools
        self.tool_registry.register("read_file", read_file)
        self.tool_registry.register("write_file", write_file)
        self.tool_registry.register("search_codebase", search_codebase)
        self.tool_registry.register("get_structure", get_structure)
        self.tool_registry.register("delete_file", delete_file)
        self.tool_registry.register("create_directory", create_directory)
        self.tool_registry.register("delete_directory", delete_directory)
        self.tool_registry.register("find_files", find_files)
        self.tool_registry.register("get_file_info", get_file_info)
        
        # Code analysis tools
        self.tool_registry.register("validate_syntax", validate_syntax)
        self.tool_registry.register("run_linter", run_linter)
        self.tool_registry.register("find_references", find_references)
        self.tool_registry.register("analyze_complexity", analyze_complexity)
        self.tool_registry.register("code_quality_report", code_quality_report)
        
        # Execution tools
        self.tool_registry.register("run_python", run_python)
        self.tool_registry.register("run_tests", run_tests)
        self.tool_registry.register("run_command", run_command)
        self.tool_registry.register("install_package", install_package)
        self.tool_registry.register("check_environment", check_environment)
        
        # Codebase analysis workflow
        self.analysis_workflow = CodebaseAnalysisWorkflow(self)
        self.tool_registry.register("comprehensive_analysis", lambda target_path=".": self.analysis_workflow.run_comprehensive_analysis(target_path))
    
    def toggle_debug(self):
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        if self.debug_mode:
            show_info("Debug mode enabled")
        else:
            show_info("Debug mode disabled")
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        show_success("Memory cleared")
    
    def show_memory_stats(self):
        """Show memory statistics"""
        stats = self.memory.get_stats()
        show_info(f"Memory Stats: {stats}")
    
    def select_tools(self, user_query: str, task_type: str = None) -> str:
        """Use specialized prompts to determine which tools to use"""
        prompt = self.prompt_manager.get_prompt_for_task(user_query, task_type)
        
        if self.debug_mode:
            detected_type = self.prompt_manager._classify_task(user_query)
            show_debug(f"Task type: {detected_type}")
        
        return self.llm.ask(prompt)
    
    def explain_code(self, file_content: str, filepath: str, user_query: str) -> str:
        """Generate an explanation of the code using specialized explanation logic"""
        context_info = self.memory.get_conversation_context()
        
        prompt = f"""
You are a code explanation expert. The user asked: "{user_query}"

{context_info}

Here is the code from {filepath}:

```
{file_content}
```

Provide a comprehensive explanation including:
1. **Main Purpose**: What this code does overall
2. **Key Components**: Important classes, functions, variables
3. **Code Flow**: How the code executes step by step
4. **Design Patterns**: Any notable patterns or techniques used
5. **Dependencies**: External libraries or modules used
6. **Potential Issues**: Areas for improvement or common pitfalls

Make it clear and educational, suitable for someone learning to code.
"""
        
        return self.llm.ask(prompt)
    
    def execute_command(self, user_query: str) -> str:
        """Enhanced execution with ReAct loop for complex tasks"""
        
        # Detect if this needs complex reasoning
        if self._needs_complex_reasoning(user_query):
            return self.react_agent.execute_task(user_query)
        else:
            # Use simple execution for basic commands
            return self._simple_execute_command(user_query)
    
    def _needs_complex_reasoning(self, query: str) -> bool:
        """Determine if query needs ReAct loop"""
        
        # Simple/direct commands that don't need reasoning
        simple_indicators = [
            query.strip().startswith(('read_file', 'write_file', 'create_directory', 'get_structure')),
            query.lower() in ['debug', 'clear memory', 'memory stats'],
            len(query.split()) <= 3 and any(word in query.lower() for word in ['read', 'write', 'create', 'run', 'show'])
        ]
        
        if any(simple_indicators):
            return False
        
        # Complex tasks that benefit from reasoning
        complex_indicators = [
            "help me", "analyze", "suggest", "improve", "create a project", 
            "build an application", "implement", "refactor", "optimize",
            "find and fix", "review", "explain how", "what does", "how to"
        ]
        
        return any(indicator in query.lower() for indicator in complex_indicators)
    
    def _simple_execute_command(self, user_query: str) -> str:
        """Simple command execution (existing logic)"""
        files_involved = []
        
        try:
            # Handle special commands
            if user_query.lower() == "clear memory":
                self.clear_memory()
                return ""
            elif user_query.lower() == "memory stats":
                self.show_memory_stats()
                return ""
            
            # Detect task type for better routing
            task_type = self.prompt_manager._classify_task(user_query)
            
            if self.debug_mode:
                show_debug(f"Detected task type: {task_type}")
            
            # Handle explanation requests with specialized logic
            if task_type == "explanation":
                filepath = self.memory.find_file_by_reference(user_query)
                
                if filepath:
                    files_involved.append(filepath)
                    file_content = read_file(filepath)
                    if not file_content.startswith("❌"):
                        explanation = self.explain_code(file_content, filepath, user_query)
                        self.memory.add_interaction(user_query, explanation, files_involved)
                        return explanation
                    else:
                        self.memory.add_interaction(user_query, file_content, files_involved)
                        return file_content
            
            # Use specialized prompts for tool selection
            tool_suggestion = self.select_tools(user_query, task_type)
            
            if self.debug_mode:
                show_debug(f"Raw LLM response: {repr(tool_suggestion)}")
            
            # Clean the tool suggestion
            tool_suggestion = tool_suggestion.strip()
            
            # Remove markdown code blocks if present
            if tool_suggestion.startswith('```'):
                lines = tool_suggestion.split('\n')
                tool_suggestion = '\n'.join(line for line in lines if not line.startswith('```'))
            
            if self.debug_mode:
                show_debug(f"Cleaned tool suggestion: {tool_suggestion}")
            
            # Execute tools
            tool_lines = [line.strip() for line in tool_suggestion.split('\n') if line.strip()]
            
            if not tool_lines:
                return "❌ No valid tool commands generated"
            
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
            
        except Exception as e:
            error_msg = f"❌ Error processing command: {e}"
            show_error(error_msg)
            return error_msg
    
    def parse_and_execute_tool(self, tool_command: str) -> str:
        """Parse and execute a single tool command"""
        try:
            # Extract tool name and parameters
            match = re.match(r'(\w+)\((.*)\)', tool_command.strip())
            if not match:
                return f"❌ Invalid tool command format: {tool_command}"
            
            tool_name = match.group(1)
            params_str = match.group(2)
            
            # Check if tool exists
            if not self.tool_registry.has_tool(tool_name):
                return f"❌ Tool '{tool_name}' not found. Available tools: {list(self.tool_registry.tools.keys())}"
            
            # Parse parameters
            params = self._parse_tool_parameters(params_str)
            
            # Execute tool
            tool_func = self.tool_registry.get_tool(tool_name)
            result = tool_func(**params)
            
            return result
            
        except Exception as e:
            return f"❌ Error executing tool '{tool_command}': {e}"
    
    def _parse_tool_parameters(self, params_str: str) -> dict:
        """Parse tool parameters from string with improved handling"""
        params = {}
        
        if not params_str.strip():
            return params
        
        # Split by commas, but be smart about quotes
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        paren_count = 0
        
        for char in params_str:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_part += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_part += char
            elif char == '(' and not in_quotes:
                paren_count += 1
                current_part += char
            elif char == ')' and not in_quotes:
                paren_count -= 1
                current_part += char
            elif char == ',' and not in_quotes and paren_count == 0:
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        # Add the last part
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Parse each part
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove outer quotes
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Handle different types
                if value.lower() == "true":
                    params[key] = True
                elif value.lower() == "false":
                    params[key] = False
                elif value.startswith('[') and value.endswith(']'):
                    # Handle lists
                    list_content = value[1:-1].strip()
                    if list_content:
                        items = []
                        for item in list_content.split(','):
                            item = item.strip()
                            if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                                item = item[1:-1]
                            items.append(item)
                        params[key] = items
                    else:
                        params[key] = []
                else:
                    # Try to convert to number
                    try:
                        if '.' in value:
                            params[key] = float(value)
                        else:
                            params[key] = int(value)
                    except ValueError:
                        params[key] = value
        
        return params

    def execute_command(self, user_query: str) -> str:
        """Enhanced execution with ReAct loop for complex tasks"""
        
        # Detect if this needs complex reasoning
        if self._needs_complex_reasoning(user_query):
            return self.react_agent.execute_task(user_query)
        else:
            # Use simple execution for basic commands
            return self._simple_execute_command(user_query)
    
    def _needs_complex_reasoning(self, query: str) -> bool:
        """Determine if query needs ReAct loop"""
        
        # Simple/direct commands that don't need reasoning
        simple_indicators = [
            query.strip().startswith(('read_file', 'write_file', 'create_directory', 'get_structure')),
            query.lower() in ['debug', 'clear memory', 'memory stats'],
            len(query.split()) <= 3 and any(word in query.lower() for word in ['read', 'write', 'create', 'run', 'show'])
        ]
        
        if any(simple_indicators):
            return False
        
        # Complex tasks that benefit from reasoning
        complex_indicators = [
            "help me", "analyze", "suggest", "improve", "create a project", 
            "build an application", "implement", "refactor", "optimize",
            "find and fix", "review", "explain how", "what does", "how to"
        ]
        
        return any(indicator in query.lower() for indicator in complex_indicators)
    
    def _simple_execute_command(self, user_query: str) -> str:
        """Simple command execution (existing logic)"""
        files_involved = []
        
        try:
            # Handle special commands
            if user_query.lower() == "clear memory":
                self.clear_memory()
                return ""
            elif user_query.lower() == "memory stats":
                self.show_memory_stats()
                return ""
            
            # Handle basic greetings and conversations
            if user_query.lower().strip() in ['hi', 'hello', 'hey']:
                return "👋 Hello! I'm CodeBuddy, your AI coding assistant. I can help you with:\n\n" \
                       "📁 File operations (read, write, create)\n" \
                       "🔍 Code analysis (syntax, quality, complexity)\n" \
                       "🚀 Project creation and management\n" \
                       "🧪 Testing and execution\n" \
                       "💡 Code suggestions and improvements\n\n" \
                       "Try asking me to 'show project structure' or 'create a simple Python file'!"
            
            # Handle help requests
            if user_query.lower().strip() in ['help', 'what can you do', 'what can you help with']:
                return self._show_help()
            
            # Detect task type for better routing
            task_type = self.prompt_manager._classify_task(user_query)
            
            if self.debug_mode:
                show_debug(f"Detected task type: {task_type}")
            
            # Handle explanation requests with specialized logic
            if task_type == "explanation":
                filepath = self.memory.find_file_by_reference(user_query)
                
                if filepath:
                    files_involved.append(filepath)
                    file_content = read_file(filepath)
                    if not file_content.startswith("❌"):
                        explanation = self.explain_code(file_content, filepath, user_query)
                        self.memory.add_interaction(user_query, explanation, files_involved)
                        return explanation
                    else:
                        self.memory.add_interaction(user_query, file_content, files_involved)
                        return file_content
            
            # Use specialized prompts for tool selection
            tool_suggestion = self.select_tools(user_query, task_type)
            
            if self.debug_mode:
                show_debug(f"Raw LLM response: {repr(tool_suggestion)}")
            
            # Clean the tool suggestion
            tool_suggestion = tool_suggestion.strip()
            
            # Remove markdown code blocks if present
            if tool_suggestion.startswith('```'):
                lines = tool_suggestion.split('\n')
                tool_suggestion = '\n'.join(line for line in lines if not line.startswith('```'))
            
            if self.debug_mode:
                show_debug(f"Cleaned tool suggestion: {tool_suggestion}")
            
            # Execute tools
            tool_lines = [line.strip() for line in tool_suggestion.split('\n') if line.strip()]
            
            if not tool_lines:
                return "❌ No valid tool commands generated"
            
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
            
        except Exception as e:
            error_msg = f"❌ Error processing command: {e}"
            show_error(error_msg)
            return error_msg
    
    def parse_and_execute_tool(self, tool_command: str) -> str:
        """Parse and execute a single tool command"""
        try:
            # Extract tool name and parameters
            match = re.match(r'(\w+)\((.*)\)', tool_command.strip())
            if not match:
                return f"❌ Invalid tool command format: {tool_command}"
            
            tool_name = match.group(1)
            params_str = match.group(2)
            
            # Check if tool exists
            if not self.tool_registry.has_tool(tool_name):
                return f"❌ Tool '{tool_name}' not found. Available tools: {list(self.tool_registry.tools.keys())}"
            
            # Parse parameters
            params = self._parse_tool_parameters(params_str)
            
            # Execute tool
            tool_func = self.tool_registry.get_tool(tool_name)
            result = tool_func(**params)
            
            return result
            
        except Exception as e:
            return f"❌ Error executing tool '{tool_command}': {e}"
    
    def _parse_tool_parameters(self, params_str: str) -> dict:
        """Parse tool parameters from string with improved handling"""
        params = {}
        
        if not params_str.strip():
            return params
        
        # Split by commas, but be smart about quotes
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        paren_count = 0
        
        for char in params_str:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_part += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_part += char
            elif char == '(' and not in_quotes:
                paren_count += 1
                current_part += char
            elif char == ')' and not in_quotes:
                paren_count -= 1
                current_part += char
            elif char == ',' and not in_quotes and paren_count == 0:
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        # Add the last part
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Parse each part
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove outer quotes
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Handle different types
                if value.lower() == "true":
                    params[key] = True
                elif value.lower() == "false":
                    params[key] = False
                elif value.startswith('[') and value.endswith(']'):
                    # Handle lists
                    list_content = value[1:-1].strip()
                    if list_content:
                        items = []
                        for item in list_content.split(','):
                            item = item.strip()
                            if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                                item = item[1:-1]
                            items.append(item)
                        params[key] = items
                    else:
                        params[key] = []
                else:
                    # Try to convert to number
                    try:
                        if '.' in value:
                            params[key] = float(value)
                        else:
                            params[key] = int(value)
                    except ValueError:
                        params[key] = value
        
        return params

    def _show_help(self) -> str:
        """Show available commands and tools"""
        return "🛠️ I can assist you with the following tasks:\n\n" \
               "📁 **File Operations**: Read, write, search, and manage files and directories.\n" \
               "🔍 **Code Analysis**: Check syntax, run linters, find references, and analyze complexity.\n" \
               "🚀 **Execution**: Run Python code, execute tests, and run shell commands.\n" \
               "📊 **Code Quality**: Get code quality reports and suggestions for improvements.\n" \
               "💾 **Memory Management**: Clear memory, show memory stats, and manage conversation history.\n\n" \
               "💡 **Tips**: Try asking me to 'show project structure', 'create a new file', or 'analyze code quality'!"