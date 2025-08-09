from typing import Dict, List, Optional
from memory.memory_manager import ConversationMemory

class PromptManager:
    def __init__(self, memory: ConversationMemory):
        self.memory = memory
        self.prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, str]:
        """Initialize all specialized prompts"""
        return {
            "file_operations": self._get_file_operations_prompt(),
            "code_analysis": self._get_code_analysis_prompt(),
            "code_execution": self._get_execution_prompt(),
            "code_generation": self._get_code_generation_prompt(),
            "explanation": self._get_explanation_prompt(),
            "debugging": self._get_debugging_prompt(),
            "project_management": self._get_project_management_prompt(),
            "general_task": self._get_general_task_prompt()
        }
    
    def get_prompt_for_task(self, user_query: str, task_type: str = None) -> str:
        """Get the appropriate prompt for a task"""
        if not task_type:
            task_type = self._classify_task(user_query)
        
        context_info = self.memory.get_conversation_context()
        base_prompt = self.prompts.get(task_type, self.prompts["general_task"])
        
        return base_prompt.format(
            user_query=user_query,
            context_info=context_info
        )
    
    def _classify_task(self, user_query: str) -> str:
        """Classify the user query into a task category"""
        query_lower = user_query.lower()
        
        # Project management (prioritize project creation)
        project_keywords = ['create a', 'create flask', 'project', 'structure', 'organize', 'setup', 'initialize', 'web application']
        if any(keyword in query_lower for keyword in project_keywords):
            return "project_management"
        
        # Code generation (prioritize this for "write" commands)
        generation_keywords = ['write a file', 'create a file', 'generate', 'build', 'make a class', 'create class', 'write class']
        if any(keyword in query_lower for keyword in generation_keywords):
            return "code_generation"
        
        # File operations
        file_keywords = ['read', 'delete', 'find', 'search', 'structure', 'directory']
        if any(keyword in query_lower for keyword in file_keywords):
            return "file_operations"
        
        # Code analysis
        analysis_keywords = ['syntax', 'lint', 'complexity', 'quality', 'analyze', 'check', 'validate', 'references']
        if any(keyword in query_lower for keyword in analysis_keywords):
            return "code_analysis"
        
        # Code execution
        execution_keywords = ['run', 'execute', 'test', 'install', 'command', 'environment']
        if any(keyword in query_lower for keyword in execution_keywords):
            return "code_execution"
        
        # Explanations
        explanation_keywords = ['explain', 'understand', 'what does', 'how does', 'describe', 'breakdown']
        if any(keyword in query_lower for keyword in explanation_keywords):
            return "explanation"
        
        # Debugging
        debug_keywords = ['error', 'bug', 'fix', 'problem', 'issue', 'debug', 'troubleshoot']
        if any(keyword in query_lower for keyword in debug_keywords):
            return "debugging"
        
        return "general_task"
    
    def _get_code_generation_prompt(self) -> str:
        return """You are a code generation specialist. A user asked: "{user_query}"

{context_info}

Available tools:
- write_file(filepath="path/to/file.py", content="code here")

CRITICAL RULES:
1. Respond with ONLY ONE write_file command
2. Keep the content simple and clean
3. Use single quotes for the content parameter: content='code here'
4. Use \\n for newlines inside the content
5. Escape single quotes inside content as \\'

Example:
write_file(filepath="calculator.py", content='class Calculator:\\n    def __init__(self):\\n        pass\\n\\n    def add(self, a, b):\\n        return a + b')

Generate a single write_file command with clean, working code."""

    def _get_file_operations_prompt(self) -> str:
        return """You are a file operations specialist. A user asked: "{user_query}"

{context_info}

Available file tools:
- read_file(filepath="path/to/file")
- search_codebase(search_term="text", directory=".")
- get_structure(directory=".")
- find_files(pattern="*.py", directory=".", max_results=20)
- get_file_info(filepath="path/to/file")
- delete_file(filepath="path/to/file")
- create_directory(directory_path="path")
- delete_directory(directory_path="path")

CRITICAL: Respond with ONLY tool commands, no explanatory text.
Example: read_file(filepath="main.py")"""

    def _get_code_analysis_prompt(self) -> str:
        return """You are a code analysis expert. A user asked: "{user_query}"

{context_info}

Available analysis tools:
- validate_syntax(filepath="path/to/file")
- run_linter(filepath="path/to/file", linter_type="auto")
- find_references(symbol="function_name", directory=".", file_extensions=[".py"])
- analyze_complexity(filepath="path/to/file")
- code_quality_report(directory=".")

CRITICAL: Respond with ONLY tool commands, no explanatory text.
Example: validate_syntax(filepath="calculator.py")"""

    def _get_execution_prompt(self) -> str:
        return """You are a code execution specialist. A user asked: "{user_query}"

{context_info}

Available execution tools:
- run_python(filepath="script.py", args=[], timeout=30)
- run_tests(test_path=".", framework="auto", timeout=60)
- run_command(command="command", working_dir=".", timeout=30, safe_mode=True)
- install_package(package_name="package", package_manager="auto", upgrade=False)
- check_environment()

CRITICAL: Respond with ONLY tool commands, no explanatory text.
Example: run_python(filepath="main.py")"""

    def _get_explanation_prompt(self) -> str:
        return """You are a code explanation expert. A user asked: "{user_query}"

{context_info}

For explanations, first read the file:
- read_file(filepath="path/to/file")

CRITICAL: Respond with ONLY the read_file command, no explanatory text.
Example: read_file(filepath="agent.py")"""

    def _get_debugging_prompt(self) -> str:
        return """You are a debugging specialist. A user asked: "{user_query}"

{context_info}

Available debugging tools:
- read_file(filepath="path/to/file")
- validate_syntax(filepath="path/to/file")
- run_linter(filepath="path/to/file", linter_type="auto")
- run_python(filepath="script.py", timeout=30)

CRITICAL: Respond with ONLY tool commands, no explanatory text.
Example: validate_syntax(filepath="main.py")"""

    def _get_project_management_prompt(self) -> str:
        return """You are a project management specialist. A user asked: "{user_query}"

{context_info}

Available project tools:
- get_structure(directory=".")
- create_directory(directory_path="path")
- write_file(filepath="path/file.ext", content="content")
- find_files(pattern="*", directory=".", max_results=50)
- code_quality_report(directory=".")

For project creation, use create_directory and write_file tools only.
Do NOT use shell commands like mkdir or touch.

CRITICAL: Respond with ONLY tool commands, no explanatory text.
Example: 
create_directory(directory_path="project_name")
create_directory(directory_path="project_name/models")
write_file(filepath="project_name/app.py", content="# Flask app")"""

    def _get_general_task_prompt(self) -> str:
        return """You are a development assistant. A user asked: "{user_query}"

{context_info}

Choose the most appropriate tools. Available:
- read_file(filepath="path"), write_file(filepath="path", content="code")
- validate_syntax(filepath="path"), run_python(filepath="script.py")
- get_structure(directory="."), create_directory(directory_path="path")

CRITICAL: Respond with ONLY tool commands, no explanatory text."""