from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def ask(self, prompt: str) -> str:
        pass

# Gemini implementation using google-generativeai
import google.generativeai as genai
from typing import Optional

class GeminiProvider:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", mock_mode: bool = False):
        self.mock_mode = mock_mode
        if not mock_mode:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
    
    def ask(self, prompt: str) -> str:
        if self.mock_mode:
            return self._mock_response(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Auto-fallback to mock mode on quota exceeded
            if "quota" in str(e).lower() or "429" in str(e):
                print("[INFO] API quota exceeded, switching to mock mode")
                self.mock_mode = True
                return self._mock_response(prompt)
            return f"Error from LLM: {e}"
    
    def _mock_response(self, prompt: str) -> str:
        """Mock responses for testing when API is unavailable"""
        prompt_lower = prompt.lower()
        
        if "structure" in prompt_lower or "get_structure" in prompt_lower:
            return 'get_structure(directory=".")'
        elif "read" in prompt_lower and "main.py" in prompt_lower:
            return 'read_file(filepath="main.py")'
        elif "write" in prompt_lower and "file" in prompt_lower:
            if "hello" in prompt_lower:
                return 'write_file(filepath="hello.py", content="print(\\"Hello World!\\")")'
            else:
                return 'write_file(filepath="test.py", content="# Mock generated code\\nprint(\\"Mock mode active\\")")'
        elif "search" in prompt_lower:
            return 'search_codebase(search_term="TODO")'
        elif "create" in prompt_lower and "directory" in prompt_lower:
            return 'create_directory(directory_path="test_dir")'
        elif "delete" in prompt_lower:
            return 'delete_file(filepath="test.py")'
        else:
            return 'get_structure(directory=".")'