from abc import ABC, abstractmethod
import google.generativeai as genai

class LLMProvider(ABC):
    @abstractmethod
    def ask(self, prompt: str) -> str:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.api_key = api_key
        self.model_name = model_name
        if not mock_mode and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
            except Exception as e:
                print(f"[WARNING] Failed to initialize Gemini: {e}")
                self.mock_mode = True

    def ask(self, prompt: str) -> str:
        if self.mock_mode:
            return self._mock_response(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "No response generated"
        except Exception as e:
            # Auto-fallback to mock mode on quota exceeded
            if "quota" in str(e).lower() or "429" in str(e) or "resource_exhausted" in str(e).lower():
                print("[INFO] API quota exceeded, switching to mock mode")
                self.mock_mode = True
                return self._mock_response(prompt)
            elif "api_key" in str(e).lower():
                print("[ERROR] Invalid API key, switching to mock mode")
                self.mock_mode = True
                return self._mock_response(prompt)
            return f"Error from LLM: {e}"
    
    def _mock_response(self, prompt: str) -> str:
        """Intelligent mock responses that can decide between conversation and tools"""
        prompt_lower = prompt.lower()
        
        # Check if this is a conversational query that doesn't need tools
        conversational_patterns = [
            "hi", "hello", "hey", "how are you", "who are you", "what are you",
            "help", "what can you do", "capabilities", "thanks", "thank you",
            "bye", "goodbye", "how's it going", "what's up"
        ]
        
        if any(pattern in prompt_lower for pattern in conversational_patterns):
            # Respond conversationally
            if any(greeting in prompt_lower for greeting in ["hi", "hello", "hey"]):
                return "Hello! I'm CodeBuddy, your AI coding assistant. How can I help you today?"
            
            elif "how are you" in prompt_lower:
                return "I'm doing great, thanks for asking! I'm here and ready to help you with any coding tasks or questions you might have. What can I assist you with today?"
            
            elif any(identity in prompt_lower for identity in ["who are you", "what are you"]):
                return """I'm CodeBuddy, an AI coding assistant designed to help developers with:

🔧 **File Operations**: Read, write, create, and manage project files
📊 **Code Analysis**: Syntax checking, linting, complexity analysis  
🚀 **Project Management**: Structure visualization, codebase search
🧪 **Testing & Execution**: Run Python code, tests, install packages
💡 **Code Assistance**: Generate code, debug issues, provide suggestions

I can handle both conversational questions and execute development tasks. What would you like to work on?"""
            
            elif any(help_word in prompt_lower for help_word in ["help", "what can you do", "capabilities"]):
                return """I can help you with various coding tasks:

**Conversational Support:**
- Answer questions about code and programming
- Explain concepts and provide guidance
- Discuss project architecture and best practices

**Development Tools:**
- File operations (read/write/create)
- Code analysis and quality checks
- Project structure visualization
- Codebase search and navigation
- Python execution and testing
- Package management

Just ask me anything or try commands like:
- "Show me the project structure"
- "Create a Python calculator"
- "Find all TODO comments"
- "Run tests in this directory" """
            
            elif any(thanks in prompt_lower for thanks in ["thank", "thanks"]):
                return "You're welcome! Happy to help with your coding projects. 😊"
            
            elif any(bye in prompt_lower for bye in ["bye", "goodbye"]):
                return "Goodbye! Feel free to come back anytime you need coding assistance. Happy coding! 👋"
            
            else:
                return "I'm here to help! What coding task can I assist you with today?"
        
        # For task-oriented queries, suggest tools
        elif "structure" in prompt_lower:
            return 'get_structure(directory=".")'
        elif "read" in prompt_lower and any(ext in prompt_lower for ext in [".py", ".js", ".html", ".css"]):
            words = prompt_lower.split()
            filename = next((word for word in words if any(ext in word for ext in [".py", ".js", ".html", ".css"])), "main.py")
            return f'read_file(filepath="{filename}")'
        elif "create" in prompt_lower and "file" in prompt_lower:
            return 'write_file(filepath="new_file.py", content="# Generated by CodeBuddy\\nprint(\\"Hello from CodeBuddy!\\")")'
        elif "search" in prompt_lower:
            search_term = "TODO"
            if "todo" in prompt_lower:
                search_term = "TODO"
            elif "function" in prompt_lower:
                search_term = "def "
            elif "class" in prompt_lower:
                search_term = "class "
            return f'search_codebase(search_term="{search_term}")'
        elif "test" in prompt_lower:
            return 'run_tests(directory=".")'
        
        # Default: provide helpful conversational response
        else:
            return """I'm here to help with your coding needs! I can:

• Answer questions and have conversations about programming
• Use tools for specific tasks like file operations, code analysis, testing
• Help with project management and development workflows

What would you like to work on? You can ask me anything or request specific actions!"""

# Factory function for easy provider creation
def create_llm_provider(provider_type: str = "gemini", **kwargs) -> LLMProvider:
    """Factory function to create LLM providers"""
    if provider_type.lower() == "gemini":
        return GeminiProvider(**kwargs)
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")