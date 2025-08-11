"""
LLM Client - Clean abstraction for Google Gemini integration
"""
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import google.generativeai as genai


class LLMClient(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM is available and working"""
        pass


class GeminiClient(LLMClient):
    """Google Gemini LLM client with intelligent fallbacks"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model
        self.model = None
        self._mock_mode = False
        
        # Try to initialize Gemini
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                # Test with a simple call
                test_response = self.model.generate_content("Hello")
                if test_response and test_response.text:
                    print("✅ Gemini LLM initialized successfully")
                else:
                    raise Exception("No response from Gemini")
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {e}")
                print("🔄 Falling back to mock mode")
                self._mock_mode = True
        else:
            print("⚠️  No Gemini API key found")
            print("🔄 Using mock mode")
            self._mock_mode = True
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response with automatic fallback"""
        if self._mock_mode:
            return self._mock_response(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            else:
                print("⚠️  Empty response from Gemini, using mock")
                return self._mock_response(prompt)
                
        except Exception as e:
            print(f"⚠️  Gemini error: {e}")
            print("🔄 Falling back to mock mode")
            self._mock_mode = True
            return self._mock_response(prompt)
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return not self._mock_mode and self.model is not None
    
    def _mock_response(self, prompt: str) -> str:
        """Intelligent mock responses for development"""
        prompt_lower = prompt.lower()

        # Extract the actual user request from the prompt
        user_request = ""
        if 'user request:' in prompt_lower:
            start = prompt_lower.find('user request:') + len('user request:')
            end = prompt_lower.find('\n', start)
            if end == -1:
                end = len(prompt_lower)
            user_request = prompt_lower[start:end].strip(' "')
        else:
            user_request = prompt_lower

        # Folder operations (check first to avoid conflict with file creation)
        if "create" in user_request and ("folder" in user_request or "directory" in user_request):
            import re
            # Extract folder name from request
            words = user_request.split()
            folder_name = "new_folder"
            for i, word in enumerate(words):
                if word in ["folder", "directory"] and i + 1 < len(words):
                    folder_name = words[i + 1]
                    break
            return f"create_folder(folderpath='{folder_name}')"

        # File writing requests (check user request specifically)
        elif "write" in user_request or ("create" in user_request and ("file" in user_request or ".py" in user_request or ".txt" in user_request)):
            # Extract filename from user request
            import re
            filename_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*\.py)', user_request)
            filename = filename_match.group(1) if filename_match else 'new_file.py'

            # Generate appropriate content based on request
            if "hello" in user_request:
                content = 'print("Hello, World!")'
            elif "calculator" in user_request:
                content = '''# Simple calculator
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

if __name__ == "__main__":
    print("Simple Calculator")
    a = float(input("Enter first number: "))
    op = input("Enter operation (+, -, *, /): ")
    b = float(input("Enter second number: "))

    if op == "+":
        print(f"Result: {add(a, b)}")
    elif op == "-":
        print(f"Result: {subtract(a, b)}")
    elif op == "*":
        print(f"Result: {multiply(a, b)}")
    elif op == "/":
        print(f"Result: {divide(a, b)}")
    else:
        print("Invalid operation")'''
            else:
                content = f'# {filename} - Created by CodingAgent\\nprint("File created successfully!")'

            return f'write_file(filepath="{filename}", content="""{content}""")'

        # File reading requests
        elif "read" in user_request or "show" in user_request:
            filename_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z]+)', user_request)
            filename = filename_match.group(1) if filename_match else 'main.py'
            return f"read_file(filepath='{filename}')"

        # List files requests
        elif "list" in user_request:
            return "list_files(directory='.')"



        # Delete operations
        elif "delete" in user_request or "remove" in user_request:
            if "folder" in user_request or "directory" in user_request:
                import re
                folder_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_/\\]*)', user_request)
                folder_name = folder_match.group(1) if folder_match else 'folder_to_delete'
                return f"delete_folder(folderpath='{folder_name}')"
            else:
                import re
                file_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_./\\]*\.[a-zA-Z]+)', user_request)
                filename = file_match.group(1) if file_match else 'file_to_delete.txt'
                return f"delete_file(filepath='{filename}')"

        # Code execution
        elif "run" in user_request or "execute" in user_request:
            if "python" in user_request or ".py" in user_request:
                import re
                file_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_./\\]*\.py)', user_request)
                filename = file_match.group(1) if file_match else 'main.py'
                return f"run_python(filepath='{filename}')"
            else:
                # Extract command from request
                command_words = user_request.split()
                if len(command_words) > 1:
                    command = ' '.join(command_words[1:])  # Skip "run"
                else:
                    command = 'ls'  # Default safe command
                return f"run_command(command='{command}')"

        # Syntax checking
        elif "check" in user_request and ("syntax" in user_request or "error" in user_request):
            import re
            file_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_./\\]*\.py)', user_request)
            filename = file_match.group(1) if file_match else 'main.py'
            return f"check_syntax(filepath='{filename}')"

        # Git operations
        elif "git" in user_request:
            return self._handle_git_command(user_request)

        # Analysis operations
        elif any(word in user_request for word in ["lint", "analyze", "security", "quality"]):
            return self._handle_analysis_command(user_request)

        # Code writing operations
        elif any(word in user_request for word in ["generate", "template", "refactor", "snippet"]):
            return self._handle_code_writing_command(user_request)
        
        # Analysis (fallback for other analysis requests)
        elif "analyze" in user_request:
            return "check_syntax(filepath='main.py')"
        
        # Default conversational
        else:
            return "I'm your coding assistant! I can help with files, git, code execution, and analysis. What would you like me to do?"

    def _handle_git_command(self, user_request: str) -> str:
        """Handle Git command requests in mock mode"""
        import re

        request_lower = user_request.lower()

        # Git status
        if "status" in request_lower:
            return "git_status()"

        # Git diff
        elif "diff" in request_lower:
            if "--staged" in request_lower:
                return "git_diff(staged=True)"
            else:
                # Try to extract filename
                file_match = re.search(r'git diff ([a-zA-Z_][a-zA-Z0-9_./\\]*\.[a-zA-Z]+)', user_request)
                if file_match:
                    filename = file_match.group(1)
                    return f"git_diff(filepath='{filename}')"
                else:
                    return "git_diff()"

        # Git add
        elif "add" in request_lower:
            # Extract filename or use default
            file_match = re.search(r'git add ([a-zA-Z_][a-zA-Z0-9_./\\]*(?:\.[a-zA-Z]+)?)', user_request)
            if file_match:
                filepath = file_match.group(1)
                return f"git_add(filepath='{filepath}')"
            else:
                return "git_add(filepath='.')"

        # Git commit
        elif "commit" in request_lower:
            # Extract commit message
            message_match = re.search(r'commit ["\']([^"\']+)["\']', user_request)
            if not message_match:
                message_match = re.search(r'commit (.+)', user_request)

            if message_match:
                message = message_match.group(1).strip('\'"')
                return f'git_commit(message="{message}")'
            else:
                return 'git_commit(message="Update files")'

        # Git push
        elif "push" in request_lower:
            # Extract remote and branch
            push_match = re.search(r'push (\w+)(?: (\w+))?', user_request)
            if push_match:
                remote = push_match.group(1)
                branch = push_match.group(2) if push_match.group(2) else ""
                if branch:
                    return f'git_push(remote="{remote}", branch="{branch}")'
                else:
                    return f'git_push(remote="{remote}")'
            else:
                return 'git_push()'

        # Git pull
        elif "pull" in request_lower:
            # Extract remote and branch
            pull_match = re.search(r'pull (\w+)(?: (\w+))?', user_request)
            if pull_match:
                remote = pull_match.group(1)
                branch = pull_match.group(2) if pull_match.group(2) else ""
                if branch:
                    return f'git_pull(remote="{remote}", branch="{branch}")'
                else:
                    return f'git_pull(remote="{remote}")'
            else:
                return 'git_pull()'

        # Git log
        elif "log" in request_lower:
            # Extract count
            count_match = re.search(r'log (\d+)', user_request)
            if count_match:
                count = count_match.group(1)
                return f'git_log(count={count})'
            else:
                return 'git_log()'

        # Git branch
        elif "branch" in request_lower:
            if "create" in request_lower or "new" in request_lower:
                branch_match = re.search(r'(?:create|new) (\w+)', user_request)
                if branch_match:
                    branch_name = branch_match.group(1)
                    return f'git_branch(action="create", branch_name="{branch_name}")'
                else:
                    return 'git_branch(action="create", branch_name="new-branch")'
            elif "switch" in request_lower or "checkout" in request_lower:
                branch_match = re.search(r'(?:switch|checkout) (\w+)', user_request)
                if branch_match:
                    branch_name = branch_match.group(1)
                    return f'git_branch(action="switch", branch_name="{branch_name}")'
                else:
                    return 'git_branch(action="switch", branch_name="main")'
            elif "delete" in request_lower:
                branch_match = re.search(r'delete (\w+)', user_request)
                if branch_match:
                    branch_name = branch_match.group(1)
                    return f'git_branch(action="delete", branch_name="{branch_name}")'
                else:
                    return 'git_branch(action="delete", branch_name="branch-to-delete")'
            else:
                return 'git_branch(action="list")'

        # Default git status
        else:
            return "git_status()"

    def _handle_analysis_command(self, user_request: str) -> str:
        """Handle analysis command requests in mock mode"""
        import re

        request_lower = user_request.lower()

        # Python linting
        if "lint" in request_lower:
            file_match = re.search(r'lint ([a-zA-Z_][a-zA-Z0-9_./\\]*\.py)', user_request)
            if file_match:
                filename = file_match.group(1)
                return f"python_lint(filepath='{filename}')"
            else:
                return "python_lint(filepath='main.py')"

        # Complexity analysis
        elif "complexity" in request_lower:
            file_match = re.search(r'complexity ([a-zA-Z_][a-zA-Z0-9_./\\]*\.py)', user_request)
            if file_match:
                filename = file_match.group(1)
                return f"analyze_complexity(filepath='{filename}')"
            else:
                return "analyze_complexity(filepath='main.py')"

        # Security scanning
        elif "security" in request_lower:
            file_match = re.search(r'security (?:scan )?([a-zA-Z_][a-zA-Z0-9_./\\]*\.py)', user_request)
            if file_match:
                filename = file_match.group(1)
                return f"security_scan(filepath='{filename}')"
            else:
                return "security_scan(filepath='main.py')"

        # Dependency analysis
        elif "dependencies" in request_lower:
            return "analyze_dependencies()"

        # Code quality
        elif "quality" in request_lower:
            file_match = re.search(r'quality ([a-zA-Z_][a-zA-Z0-9_./\\]*\.py)', user_request)
            if file_match:
                filename = file_match.group(1)
                return f"code_quality(filepath='{filename}')"
            else:
                return "code_quality(filepath='main.py')"

        # Default to linting
        else:
            return "python_lint(filepath='main.py')"

    def _handle_code_writing_command(self, user_request: str) -> str:
        """Handle code writing command requests in mock mode"""
        import re

        request_lower = user_request.lower()

        # Code generation
        if "generate" in request_lower:
            # Extract description and optional filepath
            if " to " in user_request or " in " in user_request:
                # Has filepath: "generate calculator code to calculator.py"
                parts = re.split(r'\s+(?:to|in)\s+', user_request, 1)
                if len(parts) == 2:
                    description = parts[0].replace("generate", "").strip()
                    filepath = parts[1].strip()
                    return f"generate_code(description='{description}', filepath='{filepath}')"

            # No filepath: "generate calculator code"
            description = user_request.replace("generate", "").strip()
            return f"generate_code(description='{description}')"

        # Code templates
        elif "template" in request_lower:
            template_match = re.search(r'template\s+(\w+)', user_request)
            if template_match:
                template_type = template_match.group(1)
                return f"code_template(template_name='{template_type}')"
            else:
                return "code_template(template_name='python_script')"

        # Code refactoring
        elif "refactor" in request_lower:
            file_match = re.search(r'refactor\s+(?:code\s+)?([a-zA-Z_][a-zA-Z0-9_./\\]*\.py)', user_request)
            if file_match:
                filename = file_match.group(1)

                # Check for specific refactor type
                if "extract" in request_lower:
                    return f"refactor_code(filepath='{filename}', refactor_type='extract_functions')"
                elif "naming" in request_lower:
                    return f"refactor_code(filepath='{filename}', refactor_type='improve_naming')"
                elif "docstring" in request_lower:
                    return f"refactor_code(filepath='{filename}', refactor_type='add_docstrings')"
                elif "import" in request_lower:
                    return f"refactor_code(filepath='{filename}', refactor_type='optimize_imports')"
                elif "type" in request_lower and "hint" in request_lower:
                    return f"refactor_code(filepath='{filename}', refactor_type='add_type_hints')"
                else:
                    return f"refactor_code(filepath='{filename}', refactor_type='auto')"
            else:
                return "refactor_code(filepath='main.py', refactor_type='auto')"

        # Code snippets
        elif "snippet" in request_lower:
            snippet_match = re.search(r'snippet\s+(\w+)', user_request)
            if snippet_match:
                snippet_type = snippet_match.group(1)
                return f"code_snippet(snippet_type='{snippet_type}')"
            else:
                return "code_snippet(snippet_type='singleton')"

        # Default to code generation
        else:
            return f"generate_code(description='{user_request}')"


class LLMConfig:
    """Configuration for LLM client"""
    
    def __init__(self):
        self.temperature = 0.1  # Low temperature for consistent tool generation
        self.max_tokens = 2048
        self.timeout = 30
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout
        }
