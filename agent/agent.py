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
        """Enhanced execution with conversational support"""
        try:
            if self.debug_mode:
                print(f"Processing query: {user_query}")
            
            # Classify query type first
            query_type = self._classify_query_type(user_query)
            
            if self.debug_mode:
                print(f"Query type detected: {query_type}")
            
            # Handle conversational queries without tools
            if query_type == "conversational":
                return self._generate_conversational_response(user_query)
            
            # Handle tool-based queries (existing logic)
            task_type = self.prompt_manager._classify_task(user_query)
            
            if self.debug_mode:
                print(f"Task type: {task_type}")
            
            # Use ReAct for complex tasks, simple execution for basic tasks
            if self._needs_complex_reasoning(user_query):
                return self.react_agent.execute_task(user_query)
            else:
                return self._simple_execute_command(user_query, task_type)
                
        except Exception as e:
            if self.debug_mode:
                print(f"Error in execute_command: {e}")
            return f"❌ Error processing command: {e}"
    
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
    
    def _is_conversational_response(self, response: str) -> bool:
        """Check if response is conversational rather than tool commands"""
        response = response.strip()
        
        # Empty responses are not conversational
        if not response:
            return False
        
        # If it contains tool patterns, it's likely tool-based
        tool_pattern = re.compile(r'\w+\([^)]*\)')
        if tool_pattern.search(response):
            # Check if it's mostly tools vs mostly text
            tool_matches = tool_pattern.findall(response)
            text_content = tool_pattern.sub('', response).strip()
            
            # If there's substantial text content beyond tool calls, treat as conversational
            if len(text_content) > 50 and len(tool_matches) <= 2:
                return True
            # If it's mostly tool calls, treat as tools
            elif len(tool_matches) > 0:
                return False
        
        # Check for conversational indicators
        conversational_indicators = [
            "Hello!", "Hi!", "I'm", "I am", "Thanks", "Thank you", 
            "You're welcome", "How can I help", "What can I", "I can help",
            "Goodbye", "Feel free", "Happy to help", "Let me know",
            "Here's what I can do", "I'm here to", "My capabilities"
        ]
        
        if any(indicator in response for indicator in conversational_indicators):
            return True
        
        # Check if it starts with common conversational patterns
        conversational_starters = [
            "I'm", "Hello", "Hi", "Hey", "Thanks", "You're welcome", 
            "I can help", "I'm here", "What would you like", "How can I"
        ]
        
        if any(response.startswith(starter) for starter in conversational_starters):
            return True
        
        # If response contains bullet points or formatting but no tool calls, likely conversational
        if ('•' in response or '**' in response or '🔧' in response) and not tool_pattern.search(response):
            return True
        
        return False

    def _is_conversational_text(self, line: str) -> bool:
        """Check if a single line is conversational text rather than a tool call"""
        line = line.strip()
        
        # Empty lines
        if not line:
            return True
        
        # Lines that start with conversational words
        conversational_starts = [
            "Hello", "Hi", "Hey", "I'm", "I am", "Thanks", "Thank you",
            "You're welcome", "How", "What", "Where", "When", "Why",
            "Let me", "I can", "I'll", "I will", "Feel free", "Please"
        ]
        
        if any(line.startswith(start) for start in conversational_starts):
            return True
        
        # Lines with formatting but no parentheses (likely explanatory text)
        if ('•' in line or '**' in line or '🔧' in line) and '(' not in line:
            return True
        
        # Lines that are clearly sentences (contain common sentence words)
        sentence_words = ["the", "a", "an", "is", "are", "was", "were", "can", "will", "would", "should"]
        if any(f" {word} " in f" {line.lower()} " for word in sentence_words):
            return True
        
        return False

    def _simple_execute_command(self, user_query: str, task_type: str = None) -> str:
        """Simple command execution with conversational support"""
        files_involved = []
        
        try:
            # Handle special commands
            if user_query.lower() == "clear memory":
                self.clear_memory()
                return ""
            elif user_query.lower() == "memory stats":
                self.show_memory_stats()
                return ""
            
            # Use the passed task_type or detect it if not provided
            if task_type is None:
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
            
            # NEW: Check if this is a conversational response (not a tool call)
            if self._is_conversational_response(tool_suggestion):
                # Store the interaction and return the conversational response
                self.memory.add_interaction(user_query, tool_suggestion, files_involved)
                return tool_suggestion
            
            # Execute tools
            tool_lines = [line.strip() for line in tool_suggestion.split('\n') if line.strip()]
            
            if not tool_lines:
                # If no tool lines but we have content, treat as conversational
                if tool_suggestion.strip():
                    self.memory.add_interaction(user_query, tool_suggestion, files_involved)
                    return tool_suggestion
                return "❌ No valid tool commands generated"
            
            results = []
            has_valid_tools = False
            
            for tool_line in tool_lines:
                # Skip obvious conversational text
                if self._is_conversational_text(tool_line):
                    continue
                    
                if not re.match(r'\w+\(.*\)', tool_line):
                    if self.debug_mode:
                        show_debug(f"Skipping non-tool line: {tool_line}")
                    continue
                
                if tool_line.startswith(('class ', 'def ', 'import ', 'from ', 'print(', '#')):
                    if self.debug_mode:
                        show_debug(f"Skipping code line: {tool_line}")
                    continue
                
                has_valid_tools = True
                
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
            
            # If no valid tools were found, treat the whole response as conversational
            if not has_valid_tools:
                self.memory.add_interaction(user_query, tool_suggestion, files_involved)
                return tool_suggestion
            
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

    def _generate_conversational_response(self, user_query: str) -> str:
        """Generate conversational response without tools"""
        
        # Handle specific patterns
        query_lower = user_query.lower().strip()
        
        # Greetings
        if any(greeting in query_lower for greeting in ['hi', 'hello', 'hey']):
            return """👋 Hello! I'm CodeBuddy, your AI coding assistant.

I can help you with:
• 📁 **File operations**: read, write, create files and directories
• 🔍 **Code analysis**: syntax checking, quality reports, complexity analysis  
• 🚀 **Project management**: create projects, analyze codebases
• 🧪 **Testing & execution**: run Python code, install packages, run tests
• 💡 **Code explanations**: understand how code works

Try asking:
- "Show me the project structure"
- "Create a simple Python calculator"
- "Analyze the code quality of my project"
- "Explain how the agent.py file works"

What would you like me to help with?"""

        # Programming concept questions
        if query_lower.startswith('what is'):
            concept = query_lower.replace('what is', '').strip()
            
            # Use LLM for educational responses
            educational_prompt = f"""You are a coding education assistant. Explain the concept: "{concept}"

Keep the explanation:
- Clear and beginner-friendly
- Include practical examples
- Mention how it relates to software development
- Be concise but comprehensive

If it's a programming language, mention its main use cases.
If it's a concept, explain with simple examples.
"""
            return self.llm.ask(educational_prompt)
        
        # General help
        if 'help' in query_lower or 'what can you do' in query_lower:
            return self._show_help()
        
        # Default: Use LLM for general conversation
        conversational_prompt = f"""You are CodeBuddy, a helpful AI coding assistant. 

The user said: "{user_query}"

Respond helpfully and conversationally. If they're asking about programming concepts, explain them clearly. If they're making small talk, be friendly but guide them toward how you can help with coding tasks.

Keep your response concise and helpful."""
        
        return self.llm.ask(conversational_prompt)

    def _show_help(self) -> str:
        """Show comprehensive help information"""
        return """🛠️ **CodeBuddy Help - What I Can Do:**

## 📁 File Operations
- `read file.py` - Read file contents
- `write file.py with [content]` - Create/update files  
- `create directory myproject` - Make directories
- `show project structure` - Display directory tree
- `find files matching *.py` - Search for files

## 🔍 Code Analysis  
- `validate syntax of file.py` - Check Python syntax
- `analyze code quality` - Comprehensive quality report
- `check complexity of file.py` - Analyze code complexity
- `find references to MyClass` - Locate symbol usage

## 🚀 Project Management
- `create a calculator project` - Generate complete projects
- `analyze current codebase` - Comprehensive codebase analysis
- `help me build a Flask app` - Guided project creation

## 🧪 Execution & Testing
- `run file.py` - Execute Python scripts
- `install package requests` - Install Python packages  
- `run tests in tests/` - Execute test suites

## 💡 Code Understanding
- `explain how agent.py works` - Detailed code explanations
- `what is object-oriented programming` - Concept explanations

**Need something specific? Just ask naturally! I understand context and can help with complex, multi-step tasks.**"""

    def _classify_query_type(self, user_query: str) -> str:
        """Classify if query needs tools or just conversation"""
        
        # Conversational queries (no tools needed)
        conversational_patterns = [
            # Greetings
            r'^\s*(hi|hello|hey|good morning|good afternoon)\s*$',
            # Questions about concepts
            r'what is \w+',
            r'explain \w+',
            r'tell me about \w+',
            # General questions
            r'how does \w+ work',
            r'why is \w+',
            # Help requests
            r'help\s*$',
            r'what can you do',
        ]
        
        import re
        query_lower = user_query.lower().strip()
        
        for pattern in conversational_patterns:
            if re.match(pattern, query_lower):
                return "conversational"
        
        # Tool-based queries
        tool_patterns = [
            r'read|write|create|delete|show|find|search|run|execute|install',
            r'analyze|validate|check|lint|test',
            r'generate|build|make a'
        ]
        
        for pattern in tool_patterns:
            if re.search(pattern, query_lower):
                return "tool_based"
        
        # Default: if unsure, treat as conversational for better UX
        return "conversational"